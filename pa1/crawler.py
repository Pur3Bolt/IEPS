import urllib.robotparser
from io import StringIO
from math import ceil
from urllib.parse import urlparse
from socket import gethostbyname
from datetime import datetime
from time import sleep
import database.tables as tables
import requests
#from selenium import webdriver
from seleniumwire import webdriver  # Import from seleniumwire
from selenium.webdriver.chrome.options import Options
import urlcanon
import hashlib
import re
from urllib.parse import urljoin
import mimetypes
import pathlib


# import url

delay = 5
site = tables.SiteTable()
page = tables.PageTable()
image = tables.ImageTable()
ip = tables.SiteIPAddrTable()
link = tables.LinkTable()
pagedata = tables.PageDataTable()


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
        #print(db_ip)
        #print(db_ip.get('last_access'))
        if db_ip is not None:
            sleep_untill_allowed_request(db_ip.get('last_access', None), db_ip.get('delay', None))
            print("Pre-robots sleep complete")

        # make the robots.txt request
        response = requests.get(get_base_url(url) + "/robots.txt")

        # add/update time of request for this IP
        if db_ip is None:
            ip_data = {'ip_addr': site_ip,
                       'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                       'delay': delay}
            db_ip = ip.create(ip_data)
        else:
            update_ip_time(db_ip.get('id', None))

        print('status code:', response.status_code)
        robots_text = ""
        if response.status_code == 200:
            robots_text = response.text.strip()
            parse_robots_data(rp, robots_text)
            #rp.set_url(get_base_url(url) + "/robots.txt")
            #rp.read()

        print("robots_text:")
        print(robots_text)
        print("----****----")
        sm = rp.site_maps()  # get Sitemap param as list
        sm_data = ""
        if sm:
            sleep_untill_allowed_request(db_ip.get('last_access', None), db_ip.get('delay', None))
            response = requests.get(sm[0])
            update_ip_time(db_ip.get('id', None))
            sm_data = response.text.strip()
        print("sm str:", sm_data)

        print("IP:", db_ip)

        # insert domain into DB
        site_insert_data = {'domain': domain,
                            'robots_content': robots_text,
                            'sitemap_content': sm_data,
                            'site_ipaddr_id': db_ip.get('id', None)}
        print(site_insert_data)
        robots_db = site.create(site_insert_data)
        print("Inserted:", robots_db)

        # if sitemap exists, insert URLs into frontier
       #if sm is not None:
       #     for elt in sm:
          #      page_insert_data = {'site_id': robots_db.get('id'),
            #                        'page_type_code': 'FRONTIER',
              #                      'url': elt}
            #    new_page = page.create(page_insert_data)
              #  print("Page:", new_page)

    # this domain exists in the DB
    else:
        robots_db = site.get(domain=domain)
        print(robots_db)
        parse_robots_data(rp, robots_db.get('robots_content'))
        #rp.set_url(get_base_url(url) + "/robots.txt")
         #rp.read()

    # print(rp)
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


def add_to_frontier(rp, site_db, url, disallow):
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

    url = url_to_canon(url)
    if not uri_validator(url):
        print("Not a URL.")
        return None
    if not rp.can_fetch(USER_AGENT, url):
        print("Not allowed to crawl this URL.")
        return None
    if is_disallowed(disallow, url):
        print("Not allowed to crawl this URL.")
        return None
    if 'gov.si' not in urlparse(url).netloc:
        print("Not gov.si domain")
        return None
    data_type = ['DOCX', 'PDF', 'PPT', 'PPTX', 'DOC', 'OTHER']
    # TODO POGLEDAMO CE JE JE SLUCAJN DATOTEKA
    if '.' in url.rsplit('/', 1)[1] and url.rsplit('/', 1)[1].split('.')[1].upper() in data_type:
        page_insert_data = {'site_id': site_db.get("id"),
                            'page_type_code': 'BINARY',
                            'url': url}
        try:
            new_page = page.create(page_insert_data)
            page_data_insert = {'page_id': new_page.get("id"),
                            'data_type_code': url.rsplit('/', 1)[1].split('.')[1].upper(),
                            'data': None}
            new_page_data = pagedata.create(page_data_insert)
            create_link(current_page_id, new_page.get("id"))
            print("Page:", new_page)
            return new_page
        except Exception as e:
            # probably a duplicate URL in DB
            print(e)
    else:
        url_exsist_in_db = page.get(url=url)
        if url_exsist_in_db is None:
            page_insert_data = {'site_id': site_db.get("id"),
                                'page_type_code': 'FRONTIER',
                                'url': url}
            try:
                new_page = page.create(page_insert_data)
                create_link(current_page_id, new_page.get("id"))
                print("Page:", new_page)
                return new_page
            except Exception as e:
                # probably a duplicate URL in DB
                print(e)
        else:
            create_link(current_page_id, url_exsist_in_db.get("id"))


def create_link(from_id, to_id):
    try:
        link_to_insert = {'from_page': from_id,
                          'to_page': to_id
                          }
        created_link = link.create(link_to_insert)
    except Exception as e:
        # Already exsist in DB
        print(e)

def url_to_canon(url):
    parsed_url = urlcanon.parse_url(url)
    urlcanon.whatwg(parsed_url)
    parsed_url = str(parsed_url)
    if parsed_url.lower().endswith("index.html"):
        parsed_url = parsed_url[:parsed_url.index("index.html")]
    if '/' in parsed_url:
        neki2 = parsed_url.rsplit('/', 1)[1]
        if '#' in neki2:
            parsed_url = parsed_url[:parsed_url.index("#")]
        if neki2 != '' and '.' not in neki2 and not neki2.endswith('/') and not parsed_url.endswith('/'):
            parsed_url += '/'
        parsed_url = urllib.parse.unquote(parsed_url)
        ena, dva = parsed_url.split(':')
        if ' ' in dva:
            parsed_url = ena + ':' + urllib.parse.quote(dva)
    return parsed_url

def hash_function(html):
    sha_signature = \
        hashlib.sha256(html.encode()).hexdigest()
    return sha_signature

def exsist_duplicate(hash):
    exsist = page.get(html_hash=hash)
    return exsist

def create_disallow_list(site_db):
    disallow = []
    for line in str(site_db).split("\n"):
        spliting = line.split(" ")
        if (spliting[0].lower() == 'disallow:'):
            disallow.append(spliting[1])
    return disallow

def is_disallowed(disallow, url):
    for dis in disallow:
        if re.match(dis, url) is not None:
            return True, dis
    return False


def create_disallow_list(site_db):
    disallow = []
    for line in str(site_db).split("\n"):
        spliting = line.split(" ")
        if spliting[0].lower() == 'disallow:' and '*' in spliting[1]:
            disallow.append(spliting[1].replace('/', '').replace('*', '.*').replace('?', "\\?"))
    return disallow

def insert_image(page_id, filename, rp, site_db, url, disallow):
    url_exsist_in_db = page.get(url=url)
    if url_exsist_in_db is None:
        page_insert_data = {'site_id': site_db.get("id"),
                            'page_type_code': 'BINARY',
                            'url': url}
        try:
            new_page = page.create(page_insert_data)
            create_link(current_page_id, new_page.get("id"))
            print("Image:", new_page)
            image_to_insert = {'page_id': new_page.get("id"),
                               'filename': filename,
                               'content_type': filename.rsplit('.', 1)[1],
                               'data': None,
                               'accessed_time': None
                               }
            created_image = image.create(image_to_insert)
            print("Image:", created_image)
        except Exception as e:
            # probably a duplicate URL in DB
            print(e)
    else:
        create_link(current_page_id, url_exsist_in_db.get("id"))

def parse_urls_from_javascript_onclick(links):
    seznam = []
    urls = []
    for url in links:
        if 'location.href' in url.get_attribute("onclick"):
            string = url.get_attribute("onclick")
            string = string.split('location.href=')[1].replace("'", '').replace('"', '')
            seznam.append(string)
        if 'document.location' in url.get_attribute("onclick"):
            string = url.get_attribute("onclick")
            string = string.split('document.location=')[1].replace("'", '').replace('"', '')
            seznam.append(string)
    for u in seznam:
        print("Working with: " + u)
        if 'http://' in u or 'https://' in u:
            urls.append(u)
        else:
            a = urljoin(URL_TEST_2, u)
            urls.append(a)
    return urls


# TODO remove test data
URL_TEST_1 = "http://e-prostor.gov.si/"
URL_TEST_2 = "http://evem.gov.si"
URL_TEST_3 = "http://gov.si"
URL_TEST_4 = "https://www.gov.si/drzavni-organi/vlada/seje-vlade/gradiva-v-obravnavi/show/6559"


USER_AGENT = "fri-wier-agmsak"



processing_page = page.get(page_type_code='FRONTIER') #Vrne prvega v tabeli

counter = 0
while processing_page is not None and counter < 10:
    processing_page = page.update(values={'page_type_code': "PROCESSING"}, filters={'id': processing_page.get("id")}) #Update statusa v PROCESSING
    current_page_id = processing_page.get("id")
    WEB_PAGE_ADDRESS = processing_page.get("url") #Dobim url prvega

    rp, site_db = init_robot_parser(WEB_PAGE_ADDRESS)  #Parsanje  robot text matevz

    disallow = create_disallow_list(site_db.get("robots_content")) #not needed anymore after i found out...
    print(disallow)
    # Od tle nisn nic spreminjov del od Matevza
    # TODO get this data from DB (or leave it as is...) :-)
    site_ip = gethostbyname(urlparse(WEB_PAGE_ADDRESS).netloc)
    print("Site IP:", site_ip)
    db_ip = ip.get(ip_addr=site_ip)


    sleep_untill_allowed_request(db_ip.get('last_access'), delay)

    print(f"Retrieving web page URL '{WEB_PAGE_ADDRESS}'")


    options = Options()
    options.add_argument("--headless")
    options.add_argument("user-agent=" + USER_AGENT)

    WEB_DRIVER_LOCATION = "C:\\Users\\Andrej\\Downloads\\chromedriver_win32org\\chromedriver"

    driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=options)
    driver.get(WEB_PAGE_ADDRESS)


    TIMEOUT = 5
    sleep(TIMEOUT)
    status_code = 200
    is_html = False
    content_type = 'text/html'
    # TODO POGLEDAM CE JE HTML/TEXT
    for request in driver.requests:
        if request.response and request.url == driver.current_url:
            status_code = request.response.status_code
            is_html = 'text/html' in request.response.headers['Content-Type']
            content_type = request.response.headers['Content-Type']

    #  update request time for this IP in DB
    update_ip_time(db_ip.get('id'))

    if is_html:
        html = driver.page_source
        hashed_html = hash_function(html)
        page_exsist = exsist_duplicate(hashed_html)
        if page_exsist is None:
            processing_page = page.update(values={ 'html_hash': hashed_html,
                                                   'page_type_code': "HTML",
                                                   'http_status_code': status_code,
                                                   'accessed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                   'html_content': html
                                                   }, filters={'id': processing_page.get("id")})

            # Checking all URLS for a HREF TAG
            elems = driver.find_elements_by_xpath("//a[@href]")
            for e in elems:
                add_to_frontier(rp, site_db, e.get_attribute("href"), disallow)

            # # Checking all URLS for a javascript document.href, location.href
            jelems = parse_urls_from_javascript_onclick(driver.find_elements_by_xpath("//*[@onclick]"))
            for e in jelems:
                add_to_frontier(rp, site_db, e.get_attribute("href"), disallow)



            # Storing images to DB
            srcs = driver.find_elements_by_xpath("//img[@src]")
            for s in srcs:
                src = s.get_attribute("src")
                if 'gov.si' in urlparse(src).netloc:
                    insert_image(current_page_id, src.rsplit('/', 1)[1], rp, site_db, s.get_attribute("src"), disallow)

        else:
            # Updating Duplicate
            try:
                processing_page = page.update(values={ 'html_hash': hashed_html,
                                                   'page_type_code': "DUPLICATE",
                                                   'http_status_code': status_code,
                                                   'accessed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                   'html_content': None
                                                   }, filters={'id': processing_page.get("id")})
            except Exception as e:
                print(e)


    # TODO store found blob(s) to DB
    else:
        try:
            file_type = mimetypes.guess_extension(content_type) #docx, pdf
            file_name = WEB_PAGE_ADDRESS.rsplit('/', 1)[1] + file_type #filename with its extension
            processing_page = page.update(values={'html_hash': None,
                                                  'page_type_code': "BINARY",
                                                  'http_status_code': status_code,
                                                  'accessed_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                                  'html_content': None
                                                  }, filters={'id': processing_page.get("id")})

            if file_type[1:].upper() in ['PNG', 'JPG', 'GIF', 'JPEG', 'BMP', 'TIF', 'TIFF', 'SVG', 'SVGZ', 'AI', 'PSD']:
                image_to_insert = {'page_id': processing_page.get("id"),
                                   'filename': file_name,
                                   'content_type': file_type[1:],
                                   'data': None,
                                   'accessed_time': None
                                   }
                created_image = image.create(image_to_insert)
            elif file_type[1:].upper() in ['DOCX', 'PDF', 'PPT', 'PPTX', 'DOC', 'OTHER']:
                page_data_insert = {'page_id': processing_page.get("id"),
                                'data_type_code': WEB_PAGE_ADDRESS.rsplit('/', 1)[1].split('.')[1].upper(),
                                'data': None}
                new_page_data = pagedata.create(page_data_insert)
            else:
                page_data_insert = {'page_id': processing_page.get("id"),
                                'data_type_code': 'OTHER',
                                'data': None}
                new_page_data = pagedata.create(page_data_insert)
        except Exception as e:
            print(e)

    driver.close()
    counter+=1
    processing_page = page.get(page_type_code='FRONTIER')  # Vrne prvega v tabeli

