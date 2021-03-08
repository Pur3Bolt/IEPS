import urllib
import urllib.robotparser
from io import StringIO
from math import ceil
from urllib.parse import urlparse
from socket import gethostbyname
from datetime import datetime
from time import sleep
import database.tables as tables
import requests

delay = 5
site = tables.SiteTable()
page = tables.PageTable()
ip = tables.SiteIPAddrTable()


def is_new_site(url):
    """Checks if the passed URL is a new or known domain in the DB.

    Parameters
    ----------
    url : str
        The URL to be checked

    Returns
    -------
    bool
        True if site is new, False otherwise
    """
    d = urlparse(url).netloc
    return site.get(domain=d) is None


def get_base_url(url):
    """Removes all parameters from the URL except the scheme and (sub)domain

        Parameters
        ----------
        url : str
            The URL to be transformed

        Returns
        -------
        str
            The transformed URL
        """
    return urlparse(url).scheme + "://" + urlparse(url).netloc


def init_robot_parser(url):
    """Initiates the robots.txt parser. Saves new site data to DB.

        Parameters
        ----------
        url : str
            The base URL - http(s)://sub.domain.com

        Returns
        -------
        RobotFileParser
            The set-up robot parser
        """
    rp = urllib.robotparser.RobotFileParser()
    domain = urlparse(url).netloc

    # if domain is not in DB
    if is_new_site(url):
        # check if a request can be made (time ethics)
        site_ip = gethostbyname(domain)
        print("Site IP:", site_ip)
        db_ip = ip.get(ip_addr=site_ip)
        print(db_ip)
        if db_ip is not None:
            sleep_untill_allowed_request(db_ip.last_access, db_ip.delay)
            print("Pre-robots sleep complete")

        # make the robots.txt request
        response = requests.get(get_base_url(url) + "/robots.txt")
        print('status code:', response.status_code)
        robots_text = ""
        if response.status_code == 200:
            robots_text = response.text.strip()
            parse_robots_data(rp, robots_text)
        print("robots_text:")
        print(robots_text)
        print("----****----")
        sm = rp.site_maps()  # get Sitemap param as list
        sm_data = ""
        if sm:
            print("Sitemap:", sm)
            sm_data = ';'.join(sm)
        print("sm str:", sm_data)

        # add/update time of request for this IP
        if db_ip is None:
            ip_data = {'ip_addr': site_ip,
                       'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       'delay': delay}
            db_ip = ip.create(ip_data)
        else:
            db_ip = ip.update(values={'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                              filters={'id': db_ip.id})
        print("IP:", db_ip)

        # insert domain into DB
        site_insert_data = {'domain': domain,
                            'robots_content': robots_text,
                            'sitemap_content': sm_data,
                            'site_ipaddr_id': db_ip.id}
        print(site_insert_data)
        new_site = site.create(site_insert_data)
        print("Inserted:", new_site)

        # if sitemap exists, insert URLs into frontier
        if sm is not None:
            for elt in sm:
                page_insert_data = {'site_id': new_site.id,
                                    'page_type_code': 'FRONTIER',
                                    'url': elt}
                new_page = page.create(page_insert_data)
                print("Page:", new_page)

    # this domain exists in the DB
    else:
        robots_db = site.get(domain=domain)
        print(robots_db)
        parse_robots_data(rp, robots_db.robots_content)
    return rp


def parse_robots_data(rp, data):
    """Parses the passed data from robots.txt into RobotFileParser

        Parameters
        ----------
        rp : RobotFileParser
            A robot parser
        data : str
            The contents of the robots.txt file
        """
    global delay

    lines = StringIO(data).readlines()
    rp.parse(lines)  # parse robots.txt from DB
    delay = get_robots_delay(rp)


def get_robots_delay(rp):
    """Returns the amount of time to wait between requests based on robots.txt config

        Parameters
        ----------
        rp : RobotFileParser
            A robot parser which has already read the contents of the robots.txt file

        Returns
        -------
        int
            The delay to wait in seconds
        """
    delay = rp.crawl_delay(USER_AGENT)  # check if Crawl-delay param is set
    if not delay:
        rrate = rp.request_rate(USER_AGENT)  # check if Request-rate param is set
        if rrate:
            delay = ceil(rrate.seconds / rrate.requests)
        else:
            delay = 5  # if no param was set, delay will be 5 sec
    print("Crawl delay:", delay)
    return delay


def sleep_untill_allowed_request(time_old, delay):
    """Sleeps the crawler until the difference between the old time and now is greater than delay

        Parameters
        ----------
        time_old : datetime
            Time to compare to current time
        delay : int
            How many seconds need to have elapsed between the dates
        """
    difference = datetime.now() - time_old
    sleep_time = delay - difference.total_seconds()
    if sleep_time > 0:
        print("Sleeping for ", sleep_time)
        sleep(sleep_time)


# TODO remove test URLs
URL_TEST = "http://e-prostor.gov.si/admin/test"
URL_TEST_2 = "http://evem.gov.si"
URL_TEST_3 = "http://gov.si"

USER_AGENT = "fri-wier-agmsak"
WEB_PAGE_ADDRESS = "http://evem.gov.si"  # TODO update with URL from frontier

rp = init_robot_parser(WEB_PAGE_ADDRESS)

print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")

site_ip = gethostbyname(urlparse(WEB_PAGE_ADDRESS).netloc)
print("Site IP:", site_ip)
db_ip = ip.get(ip_addr=site_ip)

sleep_untill_allowed_request(db_ip.last_access, delay)

r = requests.get(WEB_PAGE_ADDRESS, headers={'User-Agent': USER_AGENT})
print(r.text)

# update request time for this IP in DB
ip.update(values={'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, filters={'id': db_ip.id})

# testing
# print(rp.can_fetch(USER_AGENT, "http://gov.si/admin/test"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/teme/koronavirus"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/admin"))
