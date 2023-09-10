from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

url = 'https://www.sciencedirect.com/science/article/pii/S0022169423009253#ab005'

# start WebDriver
browser = webdriver.Chrome()

# get source code
driver = browser.get(url)
html_content = browser.page_source
# browser.close()

given_name = driver.find_elements_by_xpath('//span[@class="given-name"]')

given_name_list = []
for p in range(len(given_name)):
    given_name_list.append(given_name[p].text)