import urllib
import urllib.robotparser
from io import StringIO
from math import ceil
from urllib.parse import urlparse
from socket import gethostbyname
from datetime import datetime
from time import sleep

test_access_time = datetime.now()
test_delay = 8


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
    domain = urlparse(url).netloc
    # TODO DB query for this domain: site.domain
    return True


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
    if is_new_site(url):
        # check if a request can be made (time ethics)
        site_ip = gethostbyname(urlparse(url).netloc)
        print("Site IP:", site_ip)
        # TODO query to DB: check last accessed time on this IP
        # TODO if no rows in response then make request immediately, else wait until allowed to make request and update time of request
        global test_access_time
        global test_delay
        if test_access_time is not None:
            sleep_untill_allowed_request(test_access_time, test_delay)

        # make the robots.txt request
        base_url = get_base_url(url)
        rp.set_url(base_url + "/robots.txt")  # set URL of robots.txt
        rp.read()
        delay = get_robots_delay(rp)
        sm = rp.site_maps()  # get Sitemap param as list
        if sm:
            print("Sitemap:", sm)
            # TODO add sitemap URLs to frontier
        # TODO query to DB: save domain[, robots_content, sitemap_content] to DB
        # TODO query to DB: save IP for this domain and last accessed time (now) - if IP not in DB add row, else update time only
        test_access_time = datetime.now()
    else:
        # TODO query to DB: site.robots_content, bellow is a dummy robots.txt
        robots_content = """User-agent: *
        Disallow: /admin
        Disallow: /resources
        Disallow: /pomoc
        Crawl-delay: 7

        Sitemap: https://www.gov.si/sitemap.xml"""
        lines = StringIO(robots_content).readlines()
        rp.parse(lines)  # parse robots.txt from DB
        delay = get_robots_delay(rp)
    return rp, delay


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
