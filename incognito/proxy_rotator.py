import requests


def send_request(session, proxy):
   try:
       response = session.get('https://www.sciencedirect.com/science/article/pii/S0022169423009253#ab005', proxies={'http': f"http://{proxy}"})
       print(response.json())
   except:
       pass


if __name__ == "__main__":
   with open('http_proxies.txt', 'r') as file:
       proxies = file.readlines()

   with requests.Session() as session:
       for proxy in proxies:
           send_request(session, proxy)