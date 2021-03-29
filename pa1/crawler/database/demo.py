from pa1.database.tables import SiteTable, PageTypeTable, PageTable

site = SiteTable()
page_type_table = PageTypeTable()
page_table = PageTable()

site_insert_data = {'domain': 'test_domain',
                    'robots_content': 'test_robots_content',
                    'sitemap_content': 'test_sitemap_content'}
site.create(site_insert_data)

# get dobi samo enega (prvega)
test_site_id = site.get(domain='test_domain')
if test_site_id:
    test_site_id = test_site_id.id

# get dobi samo enega (prvega)
html_page_type_code = page_type_table.get(code='HTML')
if html_page_type_code:
    html_page_type_code = html_page_type_code.code

page_insert_data = {'site_id': test_site_id,
                    'page_type_code': html_page_type_code,
                    'url': 'www.test.com',
                    'html_content': '<a>test</a>',
                    'http_status_code': 200,
                    'accessed_time': None}

page_table.create(page_insert_data)
# list ti vrne vse
page_table.list()

# update values kjer filters
site.update(values={'domain': 'update.to.this'}, filters={'id': test_site_id})

# left join demo -> to naredi left join med page table in site po page.site_id=site.id
page_table.join('site', kind='LEFT', on={'site_id': 'id'})
