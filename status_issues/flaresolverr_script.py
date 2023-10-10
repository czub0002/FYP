import requests

post_body = {
  "cmd": "request.get",
  "url":"https://www.sciencedirect.com/science/article/abs/pii/S0022404923001846?via%3Dihub",
  "maxTimeout": 60000
}

response = requests.post('http://localhost:8191/v1', headers={'Content-Type': 'application/json'}, json=post_body)

if response.status_code == 200:
    json_response = response.json()
    if json_response.get('status') == 'ok':

        ## Get Cookies & Clean
        cookies = json_response['solution']['cookies']
        clean_cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}

        ## Get User-Agent
        user_agent = json_response['solution']['userAgent']

        ## Make normal request
        headers={"User-Agent": user_agent}

        response = requests.get("https://www.sciencedirect.com/science/article/abs/pii/S0022404923001846?via%3Dihub", headers=headers, cookies=clean_cookies_dict)
        if response.status_code == 200:
            ## ...parse data from response
            print('Success')

# https://scrapeops.io/python-web-scraping-playbook/python-flaresolverr/#install--run-flaresolverr

"""
docker run -d \
  --name=flaresolverr \
  -p 8191:8191 \
  -e LOG_LEVEL=info \
  --restart unless-stopped \
  ghcr.io/flaresolverr/flaresolverr:latest
"""