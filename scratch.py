import requests
import cloudscraper
from bs4 import BeautifulSoup

url = 'https://www.tandfonline.com/toc/twas20/36/1?nav=tocList'
# url = "https://tr.investing.com/crypto/bitcoin/btc-try?cid=1031382&__cf_chl_jschl_tk__=mwDMnxBYJ1cW7K9fW7d4wVxyw7g4eQEw67kFqN7wZhk-1637432241-0-gaNycGzNC30"

headers = {'User-Agent': 'Mozilla/5.0'}
# headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'}

scraper = cloudscraper.create_scraper()
response = scraper.get(url).text
print(response)

