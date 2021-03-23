from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver  # Import from seleniumwire
from time import sleep
import mimetypes

USER_AGENT = "fri-wier-agmsak"
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=" + USER_AGENT)

print("aaa")
WEB_DRIVER_LOCATION = "C:\\Users\\Andrej\\Downloads\\chromedriver_win32org\\chromedriver"

driver = webdriver.Chrome(WEB_DRIVER_LOCATION, options=options)
# Create a new instance of the Chrome driver

TEST_URL3 = "https://www.gov.si/"
TEST_URL4 = "http://84.39.218.201/MANDAT20/VLADNAGRADIVA.NSF/18a6b9887c33a0bdc12570e50034eb54/401a3abbdea89769c12586940037a8e7/$FILE/VG1-F.docx"
# Go to the Google home page
driver.get(TEST_URL4)
# Access requests via the `requests` attribute
TIMEOUT = 5
sleep(TIMEOUT)
status_code = 200
is_html = False
# TODO POGLEDAM CE JE HTML/TEXT
for request in driver.requests:
    if request.response:
        status_code = request.response.status_code
        is_html = 'text/html' in str(request.response.headers['Content-Type'])
        print(mimetypes.guess_extension(request.response.headers['Content-Type']))
        print(request.response.headers)
        print(request.headers)
print(status_code)
print(is_html)



#html = driver.page_source


#print(html)


