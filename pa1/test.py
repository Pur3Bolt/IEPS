import urllib
import urllib.robotparser
from io import StringIO
from math import ceil
from urllib.parse import urlparse
from socket import gethostbyname
from datetime import datetime
from time import sleep
from database.tables import SiteTable, PageTypeTable, PageTable
import requests

test_access_time = datetime.now()
test_delay = 8
site = SiteTable()
page = PageTable()


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
    return len(site.filter_site_table(['id'], domain=d)) == 0


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
    if is_new_site(url):
        # check if a request can be made (time ethics)
        site_ip = gethostbyname(domain)
        print("Site IP:", site_ip)
        # TODO query to DB: check last accessed time on this IP
        # TODO if no rows in response then make request immediately, else wait until allowed to make request and update time of request
        """global test_access_time
        global test_delay
        if test_access_time is not None:
            sleep_untill_allowed_request(test_access_time, test_delay)"""

        # make the robots.txt request
        response = requests.get(get_base_url(url) + "/robots.txt")
        # TODO query to DB: save IP for this domain and last accessed time (now) - if IP not in DB add row, else update time only
        print('status code:', response.status_code)
        robots_text = ""
        if response.status_code == 200:
            robots_text = response.text.strip()
            parse_robots_data(rp, robots_text)
        print("robots_text:")
        print(robots_text)
        print("----****----")
        delay = get_robots_delay(rp)
        print("delay", delay)
        sm = rp.site_maps()  # get Sitemap param as list
        sm_data = ""
        if sm:
            print("Sitemap:", sm)
            sm_data = ';'.join(sm)
        print("sm", sm_data)
        site_insert_data = {'domain': domain,
                            'robots_content': robots_text,
                            'sitemap_content': sm_data}
        site.insert_into_site(site_insert_data)
        new_site_id = site.filter_site_table(['id'], domain=domain)
        if new_site_id:
            new_site_id = new_site_id[0].id
        print("Inserted ID", new_site_id)
        for elt in sm:
            page_insert_data = {'site_id': new_site_id,
                                'page_type_code': 'FRONTIER',
                                'url': elt}
            page.insert_into_site(page_insert_data)
        # test_access_time = datetime.now()
    else:
        robots_db = site.filter_site_table(['robots_content'], domain=domain)
        if robots_db:
            robots_content = robots_db[0].robots_content
        print(robots_content)
        parse_robots_data(rp, robots_content)
        delay = get_robots_delay(rp)
        print(delay)
    return rp, delay


def parse_robots_data(rp, data):
    """Parses the passed data from robots.txt into RobotFileParser

        Parameters
        ----------
        rp : RobotFileParser
            A robot parser
        data : str
            The contents of the robots.txt file
        """
    lines = StringIO(data).readlines()
    rp.parse(lines)  # parse robots.txt from DB


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


URL_TEST = "http://e-prostor.gov.si/admin/test"  # TODO remove test url
WEB_PAGE_ADDRESS = "http://gov.si"  # TODO update with URL from frontier
USER_AGENT = "fri-wier-agmsak"

rp, delay = init_robot_parser(WEB_PAGE_ADDRESS)
exit(1)
# TODO query to DB: allowed to fetch site data or sleep?
WEB_PAGE_ADDRESS = "http://evem.gov.si"

print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")

sleep_untill_allowed_request(test_access_time, delay)

request = urllib.request.Request(
    WEB_PAGE_ADDRESS,
    headers={'User-Agent': USER_AGENT}
)

with urllib.request.urlopen(request) as response:
    html = response.read().decode("utf-8")
    print(f"Retrieved Web content: \n\n'\n{html}\n'")

# TODO update request time in DB for IP here (process data after, so other crawlers can make request sooner)

# testing
# print(rp.can_fetch(USER_AGENT, "http://gov.si/admin/test"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/teme/koronavirus"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/"))
# print(rp.can_fetch(USER_AGENT, "http://gov.si/admin"))
