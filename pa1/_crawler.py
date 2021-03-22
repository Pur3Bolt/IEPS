import hashlib
import mimetypes
import re
import urllib.robotparser
from datetime import datetime
from io import StringIO
from math import ceil
from socket import gethostbyname
from time import sleep
from urllib.parse import urljoin
from urllib.parse import urlparse

import requests
import urlcanon
from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver
import database.tables as tables


class Crawler:
    def __init__(self, frontier_lock, access_time_lock):
        self.USER_AGENT = "fri-wier-agmsak"
        self.WEB_DRIVER_LOCATION = "C:\\Users\\Andrej\\Downloads\\chromedriver_win32org\\chromedriver"
        self.wait_for = 5
        self.delay = 6
        self.frontier_lock = frontier_lock
        self.access_time_lock = access_time_lock
        self.DEBUG = True

        self.site_table = tables.SiteTable()
        self.page_table = tables.PageTable()
        self.image_table = tables.ImageTable()
        self.ip_table = tables.SiteIPAddrTable()
        self.link_table = tables.LinkTable()
        self.pagedata_table = tables.PageDataTable()

        self.current_page_id = None
        self.current_url = None
        self.processing_page = None

        options = Options()
        options.add_argument("--headless")
        options.add_argument("user-agent=" + self.USER_AGENT)
        self.driver = webdriver.Chrome(self.WEB_DRIVER_LOCATION, options=options)

    def is_new_site(self, url):
        d = urlparse(url).netloc
        return not self.site_table.get(domain=d)

    def get_base_url(self, url):
        return urlparse(url).scheme + "://" + urlparse(url).netloc

    def update_ip_time(self, site_id, pre_set_time=None):
        if pre_set_time is None:
            return self.ip_table.update(values={'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S')},
                                    filters={'id': site_id})
        return self.ip_table.update(values={'last_access': pre_set_time.strftime('%Y-%m-%d %H:%M:%S')},
                                    filters={'id': site_id})

    def init_robot_parser(self, url):
        rp = urllib.robotparser.RobotFileParser()
        domain = urlparse(url).netloc
        # if domain is not in DB
        if self.is_new_site(url):
            # check if a request can be made (time ethics)
            site_ip = gethostbyname(domain)
            db_ip = self.ip_table.get(ip_addr=site_ip)
            if db_ip:
                self.sleep_untill_allowed_request(db_ip.get('last_access', None), db_ip.get('delay', None))

            # make the robots.txt request
            response = requests.get(self.get_base_url(url) + "/robots.txt")
            robots_text = ""
            if response.status_code == 200:
                robots_text = response.text.strip()
                self.parse_robots_data(rp, robots_text)
            # add/update time of request for this IP
            if db_ip is None:
                ip_data = {'ip_addr': site_ip,
                           'last_access': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                           'delay': self.delay}
                db_ip = self.ip_table.create(ip_data)
            else:
                self.update_ip_time(db_ip.get('id', None))

            sm = rp.site_maps()  # get Sitemap param as list
            sm_data = ""
            if sm:
                self.sleep_untill_allowed_request(db_ip.get('last_access', None), db_ip.get('delay', None))
                response = requests.get(sm[0])
                self.update_ip_time(db_ip.get('id', None))
                sm_data = response.text.strip()

            # insert domain into DB
            site_insert_data = {'domain': domain,
                                'robots_content': robots_text,
                                'sitemap_content': sm_data,
                                'site_ipaddr_id': db_ip.get('id', None)}
            robots_db = self.site_table.create(site_insert_data)
        else:
            robots_db = self.site_table.get(domain=domain)
            self.parse_robots_data(rp, robots_db.get('robots_content'))
        return rp, robots_db

    def parse_robots_data(self, rp, data):
        lines = StringIO(data).readlines()
        rp.parse(lines)  # parse robots.txt from DB
        self.delay = self.get_robots_delay(rp)

    def get_robots_delay(self, rp):
        delay = rp.crawl_delay(self.USER_AGENT)  # check if Crawl-delay param is set
        if not delay:
            rrate = rp.request_rate(self.USER_AGENT)  # check if Request-rate param is set
            if rrate:
                delay = ceil(rrate.seconds / rrate.requests)
            else:
                delay = 6  # if no param was set, delay will be 5 sec
        return delay

    def sleep_untill_allowed_request(self, time_old, delay):
        difference = datetime.now() - time_old
        sleep_time = delay - difference.total_seconds()
        if sleep_time > 0:
            sleep(sleep_time)

    def uri_validator(self, s):
        try:
            result = urlparse(s)
            return all([result.scheme, result.netloc, result.path])
        except Exception as e:
            print('E1:', e)
            return False

    def add_to_frontier(self, rp, site_db, url, disallow):
        if not self.uri_validator(url):
            if self.DEBUG:
                print("Not a URL:", url)
            return None
        if 'gov.si' not in urlparse(url).netloc:
            if self.DEBUG:
                print("Not gov.si domain:", url)
            return None

        url = self.url_to_canon(url)

        if not rp.can_fetch(self.USER_AGENT, url):
            if self.DEBUG:
                print("RP not allowed to crawl this URL:", url)
            return None
        if self.is_disallowed(disallow, url):
            if self.DEBUG:
                print("Disallowed to crawl this URL:", url)
            return None

        data_type = ['DOCX', 'PDF', 'PPT', 'PPTX', 'DOC', 'ZIP', 'CSV', 'XLSX', 'ODS']
        image_type = ['PNG', 'JPG', 'GIF', 'JPEG', 'BMP', 'TIF', 'TIFF', 'SVG', 'SVGZ', 'AI', 'PSD']
        if '.' in url.rsplit('/', 1)[1] and url.rsplit('/', 1)[1].split('.')[1].upper() in data_type:
            page_insert_data = {'site_id': site_db.get("id"),
                                'page_type_code': 'BINARY',
                                'url': url}
            try:
                new_page = self.page_table.create(page_insert_data)
                page_data_insert = {'page_id': new_page.get("id"),
                                    'data_type_code': url.rsplit('/', 1)[1].split('.')[1].upper(),
                                    'data': None}
                self.pagedata_table.create(page_data_insert)
                self.create_link(self.current_page_id, new_page.get("id"))
                return new_page
            except Exception as e:
                print('E2:', e)
        elif '.' in url.rsplit('/', 1)[1] and url.rsplit('/', 1)[1].split('.')[1].upper() in image_type:
            page_insert_data = {'site_id': site_db.get("id"),
                                'page_type_code': 'BINARY',
                                'url': url}
            try:
                new_page = self.page_table.create(page_insert_data)
                image_to_insert = {'page_id': new_page.get("id"),
                                   'filename': url.rsplit('/', 1)[1].split('.')[0],
                                   'content_type': url.rsplit('/', 1)[1].split('.')[1].upper(),
                                   'data': None,
                                   'accessed_time': None
                                   }
                created_image = self.image_table.create(image_to_insert)
                self.create_link(self.current_page_id, new_page.get("id"))
                return new_page
            except Exception as e:
                print('E3:', e)
        else:
            url_exsist_in_db = self.page_table.get(url=url)
            if url_exsist_in_db is None:
                page_insert_data = {'site_id': site_db.get("id"),
                                    'page_type_code': 'FRONTIER',
                                    'url': url}
                try:
                    new_page = self.page_table.create(page_insert_data)
                    self.create_link(self.current_page_id, new_page.get("id"))
                    return new_page
                except Exception as e:
                    # probably a duplicate URL in DB
                    print('E4:', e)
            else:
                self.create_link(self.current_page_id, url_exsist_in_db.get("id"))

    def create_link(self, from_id, to_id):
        try:
            link_to_insert = {'from_page': from_id, 'to_page': to_id}
            self.link_table.create(link_to_insert)
        except Exception as e:
            print('E5:', e)

    def url_to_canon(self, url):
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
            if parsed_url.count(':') == 1:
                ena, dva = parsed_url.split(':')
                if ' ' in dva:
                    parsed_url = ena + ':' + urllib.parse.quote(dva)
        return parsed_url

    def hash_function(self, html):
        return hashlib.sha256(html.encode()).hexdigest()

    def exsist_duplicate(self, hash):
        return self.page_table.get(html_hash=hash)

    def is_disallowed(self, disallow, url):
        for dis in disallow:
            if re.match(dis, url) is not None:
                return True
        return False

    def create_disallow_list(self, site_db):
        disallow = []
        for line in str(site_db).replace("\r", "").split("\n"):
            spliting = line.split(" ")
            if spliting[0].lower() == 'disallow:' and '*' in spliting[1]:
                disallow.append(spliting[1].replace('/', '').replace('*', '.*').replace('?', "\\?"))
        return disallow

    def insert_image(self, page_id, filename, rp, site_db, url, disallow):
        url_exsist_in_db = self.page_table.get(url=url)
        if url_exsist_in_db is None:
            page_insert_data = {'site_id': site_db.get("id"),
                                'page_type_code': 'BINARY',
                                'url': url}
            try:
                new_page = self.page_table.create(page_insert_data)
                self.create_link(self.current_page_id, new_page.get("id"))
                image_to_insert = {'page_id': new_page.get("id"),
                                   'filename': filename,
                                   'content_type': filename.rsplit('.', 1)[1].upper(),
                                   'data': None,
                                   'accessed_time': None
                                   }
                created_image = self.image_table.create(image_to_insert)
            except Exception as e:
                print('E6:', e)
        else:
            self.create_link(self.current_page_id, url_exsist_in_db.get("id"))

    def parse_urls_from_javascript_onclick(self, links):
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
            if 'http://' in u or 'https://' in u:
                urls.append(u)
            else:
                a = urljoin(self.current_url, u)
                urls.append(a)
        return urls

    def get_next_url(self):
        with self.frontier_lock:
            self.processing_page = self.page_table.get(page_type_code='FRONTIER')
            if self.processing_page is None:  # Dodano ce slucajn ni v frontierju nic
                return False
            self.processing_page = self.page_table.update(values={'page_type_code': "PROCESSING"},
                                                          filters={'id': self.processing_page.get("id")})

    def process(self):
        while True:
            try:
                # self.processing_page = self.page_table.get(page_type_code='FRONTIER')
                # while self.processing_page is None:  # Dodano ce slucajn ni v frontierju nic
                #     sleep(20)  # sleep 20s
                #     self.processing_page = self.page_table.get(page_type_code='FRONTIER')

                # while self.processing_page:
                while True:
                    # self.processing_page = self.page_table.update(values={'page_type_code': "PROCESSING"},
                    #                                               filters={'id': self.processing_page.get("id")})
                    # get the next URL from Frontier or sleep
                    self.get_next_url()
                    while self.processing_page is None:
                        print('Sleep 20s')
                        sleep(20)
                        self.get_next_url()
                    if self.DEBUG:
                        print(self.processing_page.get('url'), datetime.now().strftime('%H:%M:%S'))

                    self.current_page_id = self.processing_page.get("id")
                    self.current_url = self.processing_page.get("url")
                    try:
                        # initialise the parser for robots.txt
                        rp, site_db = self.init_robot_parser(self.current_url)
                        if self.processing_page.get('site_id') is None:
                            self.processing_page = self.page_table.update(values={'site_id': site_db.get('id')},
                                                                          filters={'id': self.processing_page.get("id")})
                        disallow = self.create_disallow_list(site_db.get("robots_content"))

                        site_ip = gethostbyname(urlparse(self.current_url).netloc)
                    except:
                        self.processing_page = self.page_table.update(values={'page_type_code': "TRASH"},
                                                                      filters={'id': self.current_page_id})
                        # self.processing_page = self.page_table.get(page_type_code='FRONTIER')
                        print('E:', e)
                        continue

                    # db_ip = self.ip_table.get(ip_addr=site_ip)
                    # self.sleep_untill_allowed_request(db_ip.get('last_access'), self.delay) #Sleeping thread
                    # self.update_ip_time(db_ip.get('id'))

                    with self.access_time_lock:
                        if self.DEBUG:
                            print('IN:lock ', self.processing_page.get('url'), datetime.now().strftime('%H:%M:%S'))
                        while True:
                            db_ip = self.ip_table.get(ip_addr=site_ip)
                            difference = datetime.now() - db_ip.get('last_access')
                            sleep_time = self.delay - difference.total_seconds()
                            if sleep_time <= 0:
                                self.update_ip_time(db_ip.get('id'))
                                break
                            else:
                                sleep(1)
                        if self.DEBUG:
                            print('OUT:lock', self.processing_page.get('url'), datetime.now().strftime('%H:%M:%S'))

                    # code to check access time, update it immediately in DB, sleep outside the lock
                    #with self.access_time_lock:
                    #    print('IN:lock ', self.processing_page.get('url'), datetime.now().strftime('%H:%M:%S'))
                    #    db_ip = self.ip_table.get(ip_addr=site_ip)
                    #    difference = datetime.now() - db_ip.get('last_access')
                    #    sleep_time = self.delay - ceil(difference.total_seconds())
                    #    if sleep_time <= 0:
                    #        self.update_ip_time(db_ip.get('id'))
                    #    else:
                    #        self.update_ip_time(db_ip.get('id'),
                    #                            pre_set_time=datetime.now() + timedelta(seconds=sleep_time))
                    #    print('OUT:lock', self.processing_page.get('url'), datetime.now().strftime('%H:%M:%S'), sleep_time)
                    #if sleep_time > 0:
                    #    sleep(sleep_time)

                    self.driver.get(self.current_url)
                    sleep(self.wait_for)  # Loading website
                    status_code, is_html, content_type = 200, False, 'text/html'
                    for request in self.driver.requests:
                        if request.response and request.url == self.url_to_canon(self.driver.current_url):
                            status_code = request.response.status_code
                            is_html = 'text/html' in request.response.headers['Content-Type']
                            content_type = request.response.headers['Content-Type']
                            break

                    #  update request time for this IP in DB
                    if status_code != 200:
                        self.processing_page = self.page_table.update(values={'page_type_code': "TRASH",
                                                                              'http_status_code': status_code},
                                                                      filters={'id': self.current_page_id})
                        # self.processing_page = self.page_table.get(page_type_code='FRONTIER')
                        continue

                    if is_html:
                        html = self.driver.page_source
                        hashed_html = self.hash_function(html)
                        page_exists = self.exsist_duplicate(hashed_html)
                        if page_exists is None:
                            processing_page = self.page_table.update(values={'html_hash': hashed_html,
                                                                             'page_type_code': "HTML",
                                                                             'http_status_code': status_code,
                                                                             'accessed_time': datetime.now().strftime(
                                                                                 '%Y-%m-%d %H:%M:%S'),
                                                                             'html_content': html
                                                                             }, filters={'id': self.current_page_id})

                            # Checking all URLS for a HREF TAG
                            elems = self.driver.find_elements_by_xpath("//a[@href]")
                            for e in elems:
                                self.add_to_frontier(rp, site_db, e.get_attribute("href"), disallow)

                            # Checking all URLS for a javascript document.href, location.href
                            jelems = self.parse_urls_from_javascript_onclick(
                                self.driver.find_elements_by_xpath("//*[@onclick]"))
                            for e in jelems:
                                self.add_to_frontier(rp, site_db, e.get_attribute("href"), disallow)

                            # Storing images to DB
                            srcs = self.driver.find_elements_by_xpath("//img[@src]")
                            for s in srcs:
                                src = s.get_attribute("src")
                                if 'gov.si' in urlparse(src).netloc:
                                    self.insert_image(self.current_page_id, src.rsplit('/', 1)[1], rp, site_db,
                                                      s.get_attribute("src"),
                                                      disallow)
                        # duplicated page
                        else:
                            processing_page = self.page_table.update(values={'html_hash': hashed_html,
                                                                             'page_type_code': "DUPLICATE",
                                                                             'http_status_code': status_code,
                                                                             'accessed_time': datetime.now().strftime(
                                                                                 '%Y-%m-%d %H:%M:%S'),
                                                                             'html_content': None
                                                                             }, filters={'id': self.current_page_id})
                    # page type is not HTML
                    else:
                        try:
                            file_type = mimetypes.guess_extension(content_type)  # docx, pdf
                            if file_type is None:
                                file_type = 'OTHER'
                            if self.current_url[-1] == '/':
                                file_name = self.current_url
                            else:
                                file_name = self.current_url[:-1].rsplit('/', 1)[1] + file_type
                            processing_page = self.page_table.update(values={'html_hash': None,
                                                                             'page_type_code': "BINARY",
                                                                             'http_status_code': status_code,
                                                                             'accessed_time': datetime.now().strftime(
                                                                                 '%Y-%m-%d %H:%M:%S'),
                                                                             'html_content': None
                                                                             }, filters={'id': self.current_page_id})

                            if file_type[1:].upper() in ['PNG', 'JPG', 'GIF', 'JPEG', 'BMP', 'TIF', 'TIFF', 'SVG', 'SVGZ',
                                                         'AI', 'PSD']:
                                image_to_insert = {'page_id': self.current_page_id,
                                                   'filename': file_name,
                                                   'content_type': file_type[1:],
                                                   'data': None,
                                                   'accessed_time': None
                                                   }
                                created_image = self.image_table.create(image_to_insert)
                            elif file_type[1:].upper() in ['DOCX', 'PDF', 'PPT', 'PPTX', 'DOC', 'ZIP', 'CSV', 'XLSX', 'ODS']:
                                page_data_insert = {'page_id': self.current_page_id,
                                                    'data_type_code': self.current_url.rsplit('/', 1)[1].split('.')[
                                                        1].upper(),
                                                    'data': None}
                                new_page_data = self.pagedata_table.create(page_data_insert)
                            else:
                                page_data_insert = {'page_id': self.current_page_id,
                                                    'data_type_code': 'OTHER',
                                                    'data': None}
                                new_page_data = self.pagedata_table.create(page_data_insert)
                        except Exception as e:
                            print('E7:', e)

                    # self.processing_page = self.page_table.get(page_type_code='FRONTIER')

            except Exception as e:
                self.processing_page = self.page_table.update(values={'page_type_code': "TRASH",
                                                                      'html_content': e},
                                                              filters={'id': self.current_page_id})
                print('E8:', e)
            # finally:
            #     if self.DEBUG:
            #         print("FATAL CRAWLER EXCEPTION, RESTART")
            #     self.processing_page = self.page_table.update(values={'page_type_code': "TRASH"},
            #                                                   filters={'id': self.current_page_id})
            #     self.driver.quit()
            #     options = Options()
            #     options.add_argument("--headless")
            #     options.add_argument("user-agent=" + self.USER_AGENT)
            #     self.driver = webdriver.Chrome(self.WEB_DRIVER_LOCATION, options=options)
