from pa1.database.tables import SiteTable, PageTypeTable, PageTable

site = SiteTable()
page_type_table = PageTypeTable()
page_table = PageTable()

site_insert_data = {'domain': 'test_domain',
                    'robots_content': 'test_robots_content',
                    'sitemap_content': 'test_sitemap_content'}
site.insert_into_site(site_insert_data)

test_site_id = site.filter_site_table(['id'], domain='test_domain')
if test_site_id:
    test_site_id = test_site_id[0].id

html_page_type_code = page_type_table.filter_site_table(['code'], code='HTML')
if html_page_type_code:
    html_page_type_code = html_page_type_code[0].code

page_insert_data = {'site_id': test_site_id,
                    'page_type_code': html_page_type_code,
                    'url': 'www.test.com',
                    'html_content': '<a>test</a>',
                    'http_status_code': 200,
                    'accessed_time': None}

page_table.insert_into_site(page_insert_data)
page_table.read_from_site()
