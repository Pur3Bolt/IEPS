import urlcanon
import re
import string
import urllib.parse
import database.tables as tables
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
    ena, dva = parsed_url.split(':')
    if ' ' in dva:
        parsed_url = ena + ':' + urllib.parse.quote(dva)
    return parsed_url



print(url_to_canon("http://cs.indiana.edu:80/"))
print(url_to_canon("http://cs.indiana.edu"))
print(url_to_canon("http://cs.indiana.edu/People"))  #mankja / DONE
print(url_to_canon("http://cs.indiana.edu/faq.html#3")) #nesme bi # DONE
print(url_to_canon("http://cs.indiana.edu/a/./../b"))
print(url_to_canon("http://cs.indiana.edu/index.html")) #nesme bit index.html DONE
print(url_to_canon("http://cs.indiana.edu/%7Efill")) # %7 > tildo
print(url_to_canon("http://cs.indiana.edu/My file.htm"))
print(url_to_canon("http://CS.INDIANA.edu/People/"))





