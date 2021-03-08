import urllib.robotparser
from io import StringIO
from math import ceil
from urllib.parse import urlparse
from socket import gethostbyname
from datetime import datetime
from time import sleep
import database.tables as tables
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# import url

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


def update_ip_time(site_id):
    return ip.update(values={'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, filters={'id': site_id})


def init_robot_parser(url):
    """Initiates the robots.txt parser. Saves new site data to DB.

        Parameters
        ----------
        url : str
            The base URL - http(s)://sub.domain.com

        Returns
        -------
        RobotFileParser, Record
            The set-up robot parser and the Record of the query from the table site
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
            db_ip = update_ip_time(db_ip.id)
        print("IP:", db_ip)

        # insert domain into DB
        site_insert_data = {'domain': domain,
                            'robots_content': robots_text,
                            'sitemap_content': sm_data,
                            'site_ipaddr_id': db_ip.id}
        print(site_insert_data)
        robots_db = site.create(site_insert_data)
        print("Inserted:", robots_db)

        # if sitemap exists, insert URLs into frontier
        if sm is not None:
            for elt in sm:
                page_insert_data = {'site_id': robots_db.id,
                                    'page_type_code': 'FRONTIER',
                                    'url': elt}
                new_page = page.create(page_insert_data)
                print("Page:", new_page)

    # this domain exists in the DB
    else:
        robots_db = site.get(domain=domain)
        print(robots_db)
        parse_robots_data(rp, robots_db.robots_content)
    return rp, robots_db


def parse_robots_data(rp, data):
    """Parses the passed data from robots.txt into RobotFileParser and sets the global variable delay

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


def uri_validator(s):
    """Validates if the passed string is a valid URL

        Parameters
        ----------
        s : str
            The string to check if is an URL

        Returns
        -------
        bool
            True if s is a valid URL
        """
    try:
        result = urlparse(s)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False


def add_to_frontier(rp, site_db, url):
    """Adds the given URL to the frontier if permitted by rules

        Parameters
        ----------
        rp : RobotFileParser
            An initialised robots.txt parser for this site
        site_db : Record
            The DB record of this domain (from table site)
        url : str
            The URL to add to the frontier

        Returns
        -------
        mixed
            None if the URL is not allowed to be added to the frontier
            Record of the newly inserted row into DB otherwise
        """
    # TODO relative URLs must be valid; URLs must be canonicalised and cleaned
    if not uri_validator(url):
        print("Not a URL.")
        return None
    elif not rp.can_fetch(USER_AGENT, url):
        print("Not allowed to crawl this URL.")
        return None
    if 'gov.si' not in urlparse(url).netloc:
        print("Not gov.si domain")
        return None
    page_insert_data = {'site_id': site_db.id,
                        'page_type_code': 'FRONTIER',
                        'url': url}
    try:
        new_page = page.create(page_insert_data)
        print("Page:", new_page)
        return new_page
    except Exception as e:
        # probably a duplicate URL in DB
        print(e)


# TODO remove test data
URL_TEST_1 = "http://e-prostor.gov.si/"
URL_TEST_2 = "http://evem.gov.si"
URL_TEST_3 = "http://gov.si"
SELENIUM = True

USER_AGENT = "fri-wier-agmsak"
WEB_PAGE_ADDRESS = URL_TEST_3  # TODO update with URL from frontier

rp, site_db = init_robot_parser(WEB_PAGE_ADDRESS)

# TODO get this data from DB (or leave it as is...) :-)
site_ip = gethostbyname(urlparse(WEB_PAGE_ADDRESS).netloc)
print("Site IP:", site_ip)
db_ip = ip.get(ip_addr=site_ip)

sleep_untill_allowed_request(db_ip.last_access, delay)

print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")

if SELENIUM:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=" + USER_AGENT)

    WEB_DRIVER_LOCATION = "chromedriver"

    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=options)
    driver.get(WEB_PAGE_ADDRESS)

    TIMEOUT = 5
    sleep(TIMEOUT)

    # update request time for this IP in DB
    update_ip_time(db_ip.id)

    # TODO detect duplicate website here

    # TODO detect if website is HTML/text/... and save all found URLs to frontier
    elems = driver.find_elements_by_xpath("//a[@href]")
    for e in elems:
        print(e.get_attribute("href"))
        add_to_frontier(rp, site_db, e.get_attribute("href"))

    # TODO store found blob(s) to DB

    driver.close()
else:  # TODO probably remove this else block completely, since we will always use Selenium
    r = requests.get(WEB_PAGE_ADDRESS, headers={'User-Agent': USER_AGENT})

    # update request time for this IP in DB
    update_ip_time(db_ip.id)

    print(r.text)
