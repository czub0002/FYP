import asyncio
import csv

import aiohttp as aiohttp
import requests

CSV_FILENAME = 'Free_Proxy_List.csv'
url = 'https://www.tandfonline.com/doi/full/10.1080/23570008.2021.2018540'
URL_TO_CHECK = url
TIMEOUT_IN_SECONDS = 1000


async def check_proxy(url, proxy):
    try:
        session_timeout = aiohttp.ClientTimeout(total=None,
                                                sock_connect=TIMEOUT_IN_SECONDS,
                                                sock_read=TIMEOUT_IN_SECONDS)
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            async with session.get(url, proxy=proxy, timeout=TIMEOUT_IN_SECONDS) as resp:
                print(await resp.text())
    except Exception as error:
        # you can comment out this line to only see valid proxies printed out in the command line
        print('Proxy responded with an error: ', error)
        return


async def main():
    tasks = []
    with open(CSV_FILENAME) as open_file:
        reader = csv.reader(open_file)

        for csv_row in reader:
            task = asyncio.create_task(check_proxy(URL_TO_CHECK, csv_row[0]))
            tasks.append(task)

    await asyncio.gather(*tasks)

response = requests.get(url)
print(response.status_code)

asyncio.run(main())