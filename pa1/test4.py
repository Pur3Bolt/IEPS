import urlcanon
import re
import string
import urllib.parse
import database.tables as tables

from pa1.crawler_test import Crawler1

printable = set(string.printable)
def url_to_canon(url):
    parsed_url = urlcanon.parse_url(url)
    urlcanon.whatwg(parsed_url)
    parsed_url = str(parsed_url)
    if parsed_url.lower().endswith("index.html"):
        parsed_url = parsed_url[:parsed_url.index("index.html")]
    neki2 = parsed_url.rsplit('/', 1)[1]
    if '#' in neki2:
        parsed_url = parsed_url[:parsed_url.index("#")]
    if neki2 != '' and '.' not in neki2 and not neki2.endswith('/'):
        parsed_url += '/'
    parsed_url = urllib.parse.unquote(parsed_url)
    if parsed_url.count(':') == 1:
        ena, dva = parsed_url.split(':')
        if ' ' in dva:
            parsed_url = ena + ':' + urllib.parse.quote(dva)
    return parsed_url

#print("https://www.gov.si/gone?src=http://www.gu.gov.si&url=http://gu.arhiv-spletisc.gov.si/si/delovnapodrocja_gu/projekti_gu/registri/kszi/komisija/")
#print(urlcanon.parse_url("https://www.gov.si/gone?src=http://www.gu.gov.si&url=http://gu.arhiv-spletisc.gov.si/si/delovnapodrocja_gu/projekti_gu/registri/kszi/komisija/"))

#print(url_to_canon("https://www.gov.si/gone?src=http://www.gu.gov.si&url=http://gu.arhiv-spletisc.gov.si/si/delovnapodrocja_gu/projekti_gu/registri/kszi/komisija/"))


crawler = Crawler1("http://www.gu.gov.si/si/delovnapodrocja_gu/projekti_gu/registri/kszi/komisija/ ")
crawler.process()


#a = "https://www.gov.si/novice/rss?tagID=554/".rsplit('/', 1)[1]