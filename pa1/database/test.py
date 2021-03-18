from .tables import *
print("----------------- TESTS ----------------")
print("-- test -- tables init -- start")
page = PageTable()
page_type = PageTypeTable()
site = SiteTable()
print("-- test -- tables init -- pass")
print("----------------------------------------")
print("-- test -- set debug -- start")
site.set_debug(True)
if site.DEBUG:
    site.set_debug(False)
    print("-- test -- set debug -- pass")
else:
    print("-- test -- set debug -- fail")
    exit(1)
print("----------------------------------------")
print("-- test -- create -- start")
site_insert_data = {'domain': 'test_domain',
                    'robots_content': 'test_robots_content',
                    'sitemap_content': 'test_sitemap_content'}
create_site = site.create(site_insert_data)
if create_site['domain'] == site_insert_data['domain']:
    print("-- test -- create -- pass")
else:
    print("-- test -- create -- fail")
print("----------------------------------------")
print("-- test -- list -- start")
sites = site.list()
if len(sites):
    print("-- test -- list -- pass")
else:
    print("-- test -- list -- fail")
print("----------------------------------------")
print("-- test -- get -- start")
site_id = sites[0]['id']
get_site = site.get(id=site_id)
if get_site['id'] == site_id:
    print("-- test -- get -- pass")
else:
    print("-- test -- get -- fail")
print("----------------------------------------")
print("-- test -- filter -- start")
filter_site = site.filter(robots_content='test_robots_content')
if len(filter_site):
    print("-- test -- filter -- pass")
else:
    print("-- test -- filter -- fail")
print("----------------------------------------")
print("-- test -- update -- start")
try:
    page_id = page.list()[0]['id']
    html = open('database/index.html', 'r')
    page.update(values={'html_content': html.read()}, filters={'id': page_id})
except:
    print("-- test -- update -- fail")
else:
    print("-- test -- update -- pass")
print("----------------- DONE ----------------")
