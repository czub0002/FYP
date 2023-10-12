import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
import cloudscraper
from dateutil import parser
import csv
import re
import pandas as pd
import tabulate

def main():
    big_start = time.time()

    fields = ['wos_doi', 'doi', 'type', 'title', 'authors', 'received_date', 'accepted_date', 'published_date',
              'journal', 'journal_edition', 'publication_year', 'uid', 'issue', 'url', 'references']
    file_path = 'tandf_database.csv'
    start_index = 0
    path = Path(file_path)
    df = pd.read_excel('Taylor-and-Francis.xlsx')

    tandf_df = pd.read_csv(file_path)

    if not tandf_df.empty:
        last_doi = tandf_df.iloc[-1]["wos_doi"]
        matching_rows = df[df["DOI"] == last_doi]
        start_index = matching_rows.index[-1] + 1

    # TODO - Proxy/user agent rotation

    cloud_scraper = cloudscraper.create_scraper()
    counter = 0

    # keep record of status errors
    status_errors = []
    previous_identifier = (None, None, None)       # (ISSN, eISSN, ISBN)

    for index, row in df.iloc[start_index:].iterrows():
        counter += 1
        print(f"{counter} -----------------------------")

        # TODO - Remove before executing script
        if counter == 15:
            break

        # TODO - Check DOI always exists when DOI Link does in WoS database before executing script
        doi_link_value = row["DOI Link"]
        wos_doi = row["DOI"]

        if doi_link_value:
            errors_403 = [2, 4, 6, 8, 10, 12, 14]
            if counter in errors_403:
                response = requests.get(doi_link_value)
            else:
                response = cloud_scraper.get(doi_link_value)

            # status_code 200 means get was successful
            if response.status_code == 200 and 'tandfonline' in response.url:
                print('DataScraper(response, wos_doi)')
            else:
                print(f"ERROR: Status {response.status_code}")
                current_error = {"status_code": response.status_code, "index": index, "data": row}
                current_identifier = (row["ISSN"], row["eISSN"], row["ISBN"])

                if status_errors:
                    # Conditions of termination: Previous error same as current and must belong to different journals
                    # and indexes must be consecutive
                    # TODO - add journal condition back in later and confirm this is a good strategy
                    previous_error = status_errors[-1]
                    if previous_error["status_code"] == current_error["status_code"] \
                            and (current_identifier != previous_identifier) and \
                            (previous_error["index"] == current_error["index"]-1):

                        status_errors.append(current_error)

                        print("\n______________________________________________________")
                        print("-------------- Summary of Status Errors --------------")
                        header = ["Status Code", "Index", "DOI"]

                        error_list = []
                        for error in status_errors:
                            error_list.append([error["status_code"], error["index"], error["data"]["DOI"]])

                        print(tabulate.tabulate(error_list, header))

                        # Terminate program
                        print(f'\nThe script terminated due to {current_error["status_code"]} status errors!\n')
                        break

                status_errors.append(current_error)
                previous_identifier = current_identifier

    big_end = time.time()
    total_time = big_end - big_start

    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)
    print(f'Total Runtime: {h:0.0f} hours, {m:02.0f} minutes, {s:02.2f} seconds.')


if __name__ == '__main__':
    main()
