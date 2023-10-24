import requests
from requests_ip_rotator import ApiGateway, EXTRA_REGIONS

url = 'https://www.tandfonline.com/doi/full/10.1080/23570008.2021.2018540'
url_gateway = 'https://www.tandfonline.com/doi/full/10.1080/23570008.2021.2018540'


gateway = ApiGateway("https://www.tandfonline.com")
gateway.start()

session = requests.Session()
session.mount("https://www.transfermarkt.es", gateway)

response = session.get(url)
print(response.status_code)

# Only run this line if you are no longer going to run the script, as it takes longer to boot up again next time.
# gateway.shutdown()