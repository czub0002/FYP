from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

url = 'https://www.sciencedirect.com/science/article/pii/S0022169423009253#ab005'

# start WebDriver
browser = webdriver.Chrome()

# get source code
driver = browser.get(url)
html_content = browser.page_source
# browser.close()

given_name = driver.find_elements(By.XPATH, '//span[@class="given-name"]')

given_name_list = []
for p in range(len(given_name)):
    given_name_list.append(given_name[p].text)

# # Finding DOIs
# query = "doi/ref/"
# start_index = 0
# appearances = []

# author_first_name_list = [] 
# author_last_name_list = [] 

# first_name_query = "given-name\">"

# #  Find each instance of the query
# while True:
#     index = html_content.find(first_name_query, start_index)
#     if index == -1:
#         break
#     appearances.append(index)
#     start_index = index + len(first_name_query)

# # Extracting the doi from the string
# for index in appearances:
#     id_increment = index + len(first_name_query)
#     first_name = ""

#     # Checks for the end of the doi
#     while html_content[id_increment] != ('\"' or "\'"):
#         first_name += html_content[id_increment]
#         id_increment += 1

#     # Checks for duplicate doi
#     if first_name not in author_first_name_list:
#         author_first_name_list.append(first_name)

# # print("No. of unique DOIs: " + str(len(doi_list)))
# print(author_first_name_list)