from html import unescape
from urllib.parse import unquote
import requests
from bs4 import BeautifulSoup
import pandas as pd

noDOI = 0
firstPass = 0
secondPass = 0
firstFail = 0
secondFail = 0
total = 0

# start WebDriver
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

df = pd.read_excel('Elsevier.xlsx')
# If 'DOI Link' column exists in your DataFrame, you can proceed with the loop
if 'DOI Link' in df.columns:
    for index, row in df.iterrows():
        if total == 20:
            break
        total += 1
        doi_link_value = row['DOI Link']

        if doi_link_value:
            # Now 'doi_link_value' contains the value in the 'DOI Link' column for the current row
            response = requests.get(doi_link_value, headers=headers, allow_redirects=True)

            if response.status_code == 200:
                firstPass += 1
                soup = BeautifulSoup(response.text, 'html.parser')
                redirect_url = soup.find(name="input", attrs={"name": "redirectURL"})["value"]
                final_url = unescape(unquote(redirect_url))
                response = requests.get(final_url, headers=headers, allow_redirects=True)
                if response.status_code == 200:
                    secondPass += 1
                else:
                    secondFail += 1
            else:
                firstFail += 1
        else:
            noDOI += 1
else:
    print("The 'DOI Link' column does not exist in the DataFrame.")

print(f"First Pass: {firstPass}")
print(f"Second Pass: {secondPass}")
print('--------------------')
print(f"First Fail: {firstFail}")
print(f"Second Fail: {secondFail}")
print('--------------------')
print(f"Total: {total}")