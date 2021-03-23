import re


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


robots="""User-agent: *
Disallow: /e-uprava/oglasnadeska.html
Disallow: /*?view_mode* 
Disallow: /*?*bold_mode* 
Disallow: /*?caps_mode* """
robots2="""User-Agent: *
Allow: /
Disallow: /fileadmin/global/
Disallow: /fileadmin/user_upload/MVN_obcine_obrazci/
Disallow: /t3lib/
Disallow: /nc/
Disallow: *no_cache*
Disallow: /*cHash
Disallow: /typo3/
Disallow: /urednik/
Disallow: /typo3conf/
Disallow: /typo3temp/
Disallow: /*?id=*
Disallow: /*&type=98
Disallow: /*&type=100Sitemap: http://www.e-prostor.gov.si/?eID=dd_googlesitemap"""
disallow=create_disallow_list(robots)
print('Disallow:', disallow)

tests="""https://e-uprava.gov.si/?view_mode=3/
https://e-uprava.gov.si/?a=2&view_mode=4/
https://e-uprava.gov.si/?bold_mode=4/
https://e-uprava.gov.si/?a=2&bold_mode=4/
https://e-uprava.gov.si/?caps_mode=4/
https://e-uprava.gov.si/?a=2&caps_mode=4/
https://e-uprava.gov.si/danasnjeteme/ja/testiranje?view_mode=3/
/?view_mode=3/
/?a=2&view_mode=4/
/danasnjeteme/ja/testiranje?view_mode=3/""".split("\n")
tests2="""https://www.e-prostor.gov.si/informacije/vsa-pogosta-vprasanja/?no_cache=1/
https://www.mvn.e-prostor.gov.si/?id=1154/""".split("\n")
for s in tests2:
    print(s, is_disallowed(disallow, s))
