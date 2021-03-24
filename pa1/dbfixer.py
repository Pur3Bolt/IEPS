import urllib.robotparser
from urllib.parse import urljoin
import urlcanon
import database.tables as tables
import url_normalize


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
    parsed_url = url_normalize.url_normalize(parsed_url)
    return parsed_url


def exists_in_db(url, table):
    return table.get(url=url) is not None


page_table = tables.PageTable()
link_table = tables.LinkTable()
image_table = tables.ImageTable()
pagedata_table = tables.PageDataTable()
res = page_table.list(fields=['id', 'url', 'page_type_code'])
f = open("dbfixerlog.txt", "a")
# print(res[0].get('url'))
s="https://prostor4.gov.si/imps/srv/slv/catalog.search?id=2#/home"
print(s)
print(url_to_canon(s))

exit(1)
# get next url
for row in res:
    if row.get('page_type_code') in ['TRASH', 'INCORRECT']:
        continue
    # put url to canon
    canon = url_to_canon(row.get('url'))
    # is the url the same? end if yes
    if row.get('url') == canon:
        continue
    f.write("\nS: " + str(row.get('id')) + row.get('url') + "\n")
    print("S: " + str(row.get('id')) + row.get('url'))
    # check if canon url exists in db
    if exists_in_db(canon, page_table):
        f.write('E: ' + canon + "\n")
        print('E: ' + canon)
        other_url = page_table.get(url=canon)
        # check if the url is in the frontier; delete that one if yes (incl data in link)
        if other_url.get('page_type_code') in ['FRONTIER', 'DUPLICATE']:
            f.write('F ')
            try:
                link_table.delete(filters={'to_page': other_url.get('id')})
                image_table.delete(filters={'page_id': other_url.get('id')})
                pagedata_table.delete(filters={'page_id': other_url.get('id')})
                page_table.delete(filters={'id': other_url.get('id')})
                page_table.update(values={'url': canon},
                                  filters={'id': row.get('id')})
                f.write("DELETED\n")
                print("F DELETED")
            except Exception as e:
                f.write("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n")
                print('E1', e)
        # other url is not frontier; mark the data in variable row as INCORRECT, since the canon'd url was searched already
        else:
            page_table.update(values={'page_type_code': 'INCFIX'},
                              filters={'id': row.get('id')})
            f.write("INCORRECT\n")
            print("F INCORRECT")
    # there is no canon'd row in DB, just change URL for this row
    else:
        f.write('N ')
        try:
            page_table.update(values={'url': canon},
                              filters={'id': row.get('id')})
            f.write("DONE\n")
            print("N DONE")
        except Exception as e:
            print('E2', e)

f.close()
