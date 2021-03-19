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
for s in tests:
    print(s, is_disallowed(disallow, s))
