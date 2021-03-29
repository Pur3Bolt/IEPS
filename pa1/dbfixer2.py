import json
import database.tables as tables


page_table = tables.PageTable()
f = open("dbfixer2log.txt", "a")
pages_file = open('incorrect.json', 'r')
pages = json.load(pages_file)
sites_file = open('site.json', 'r')
sites = json.load(sites_file)
for page in pages:
    print(page)
    f.write(page['url'] + ' (' + str(page['id']) + ') > ')
    for site in sites:
        if '://' + site['domain'] in page['url']:
            try:
                page_table.update(values={'site_id': site['id']},
                                  filters={'id': page['id']})
            except Exception as e:
                print(e)
                f.write('EXC ' + site['domain'] + ' (' + str(site['id']) + ")\n")
            print(site)
            f.write(site['domain'] + ' (' + str(site['id']) + ")\n")
            continue
# print(pages[1])
# #print(sites[0])
# for i in range (0, len(sites)):
#     if '://'+sites[i]['domain'] in pages[1]['url']:
#         print(i, sites[i])
f.close()
