from functions import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import urllib3
import time
# Disable warnings related to insecure requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) 
# Proxy token
proxy_token = "e087f00b97cb451c8f95d1d9aafb1529e9b197dfcb6"

proxy_url = f"http://{proxy_token}:@proxy.scrape.do:8080"

def create_driver_with_proxy(proxy_url):
    """Create a new WebDriver instance with the specified proxy."""
    chrome_options = Options()
    chrome_options.add_argument(f"--proxy-server={proxy_url}")
    
    # Path to your ChromeDriver
    service = Service(executable_path="chromedriver.exe")  # Update this path

    # Initialize WebDriver with proxy settings
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver
# Initialize WebDriver with proxy
# driver = create_driver_with_proxy(proxy_url)
service = Service(executable_path="chromedriver.exe")
driver = webdriver.Chrome(service=service)

try:
    driver.get("https://amazon.com")
    # Call your functions
    solve_captcha(driver)
    change_zip_code("10001", driver)
    search("iphone", driver)
    links = search_links(driver)
    
    time.sleep(5)
    i=0
    for link in links: 
         product_info = get_product_data(driver, link)
         append_to_csv(product_info)
         i+=1
         if i==10:
             break
    product_info = get_product_data(driver, "https://www.amazon.com/13-Compatible-Anti-Yellowing-Shockproof-inch-Clear/dp/B0CC5L8XXK/ref=sr_1_164?crid=300JMPDBGPDN8&dib=eyJ2IjoiMSJ9.LXYe3uHtGN4Vmo6h0roTZATxFD3Ys3gprq6V_RAr0n96Yh1l2kjZX0aS6LwPHcuoRAEala4IzdUQCLZpr8QPf-6yy13iIm3roRN3tATZoy-9_-snJ7zQEa4kjs0vh21qmvA-YUL4mmNoOM2Zm3BoYtubjQhHhjDBizFIptGL7q0mF7v4E8L5XsmprP9ydb0f49TDExKgXrpGpUs7p6wAR2FY1ShL5QBURcT0u1O7-0E.Hc1diPFnmzA5Pgap68_F7q0BJHje_bcf-50sDwiWb5E&dib_tag=se&keywords=iphone+case&qid=1723635777&sprefix=iphone+ca%2Caps%2C519&sr=8-164")
    append_to_csv(product_info)
finally:
    
    driver.quit()
