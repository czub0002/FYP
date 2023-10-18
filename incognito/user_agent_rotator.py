import requests
from fake_useragent import UserAgent
import time
import cloudscraper

url = 'https://www.tandfonline.com/doi/full/10.1080/23570008.2021.2018540'
scraper = cloudscraper.create_scraper().get(url)
print(f"cookies: {scraper.cookies}")
print(f"request.headers: {scraper.request.headers}")

getter = requests.get(url, headers=scraper.request.headers, cookies=scraper.cookies)
print(getter)

#
# # Create a UserAgent object
# ua = UserAgent()
#
# # Example list of target URLs
# urls = [url]
#
# # Make requests with rotating user agents
# for url in urls:
#     # Generate a random user agent
#     headers = {'User-Agent': ua.random}
#
#     # Make the request
#     response = requests.get(url, headers=headers)
#
#     # Process the response
#     if response.status_code == 200:
#         print(f"Success for {url}")
#         # Your processing logic here
#     else:
#         print(f"Error for {url}. Status code: {response.status_code}")
#
#     # Pause for a short time to avoid rate limiting or getting blocked
#     time.sleep(2)
