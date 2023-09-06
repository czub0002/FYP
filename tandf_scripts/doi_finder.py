from selenium import webdriver

url = 'https://www.tandfonline.com/toc/twas20/36/1?nav=tocList'

# start WebDriver
browser = webdriver.Chrome()

# get source code
browser.get(url)
html_content = browser.page_source
browser.close()

# Finding DOIs
query = "doi/ref/"
start_index = 0
appearances = []
doi_list = []

# Find each instance of the query
while True:
    index = html_content.find(query, start_index)
    if index == -1:
        break
    appearances.append(index)
    start_index = index + len(query)

# Extracting the doi from the string
for index in appearances:
    id_increment = index + len(query)
    doi = ""

    # Checks for the end of the doi
    while html_content[id_increment] != ('\"' or "\'"):
        doi += html_content[id_increment]
        id_increment += 1

    # Checks for duplicate doi
    if doi not in doi_list:
        doi_list.append(doi)

print("No. of unique DOIs: " + str(len(doi_list)))
print(doi_list)
