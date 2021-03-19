from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
import pathlib
from urllib.parse import urljoin
import database.tables as tables
page = tables.PageTable()
datatype = tables.DataTypeTable()
URL_TEST_2 = "https://www.gov.si/"
URL_TEST_3 = "https://www.gov.si/drzavni-organi/vlada/seje-vlade/gradiva-v-obravnavi/show/6559"
URL_TEST_4 = "http://84.39.218.201/MANDAT20/VLADNAGRADIVA.NSF/18a6b9887c33a0bdc12570e50034eb54/401a3abbdea89769c12586940037a8e7/$FILE/VG1-F.docx"
URL_TEST_5 = "C:\\Users\\Andrej\\Desktop\\FAKS\\IEPS\\IEPS\\pa1\\test.html"
SELENIUM = True

USER_AGENT = "fri-wier-agmsak"
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=" + USER_AGENT)
print("aaa")
WEB_DRIVER_LOCATION = "C:\\Users\\Andrej\\Downloads\\chromedriver_win32org\\chromedriver"

driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=options)
driver.get(URL_TEST_5)


html = driver.page_source
#print(html)
tabela = ['DOCX', 'PDF', 'PPT', 'PPTX', 'DOC']
a = datatype.list2()
print(a)
links = driver.find_elements_by_xpath("//*[@onclick]")
seznam = []
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
    print("Working with: " + u)
    if 'http://' in u or 'https://' in u:
        print(u)
    else:
        a = urljoin(URL_TEST_2, u)
        print(a)


print(URL_TEST_5)

page_insert_data = {'site_id': 105,
                    'page_type_code': 'FRONTIER',
                    'url': URL_TEST_3,
                    'html_content': html }

#page.set_debug(True)
#new_page = page.create(page_insert_data)
#print(new_page)

#page.update(values={'html_content': html}, filters={'id': 3283})