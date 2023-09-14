"""
Script runs through wos core journal lists and calls clarivate_API_test.py to perform WoS API requests to extract
the relevant data. This is then stored in a csv (depending on the publisher) to build the database.
"""

import csv
import sys

import starter_API_getter
import time

start_time = time.time()

publishers = ["elsevier", "springer", ["taylor", "francis"], "wiley"]
# core_files = ["wos-core_SCIE 2023-August-22.csv", "wos-core_SSCI_2023-August-22.csv"]
core_file = "wos-core_SCIE 2023-August-22.csv"

# Creating a csv for WOS database - one for each publisher
for publisher in publishers:
    if type(publisher) is list:
        publisher = 'tandf'
    with open(f"{publisher}.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Create header for WoS data
        # TODO - update after determining the data to pull
        fieldnames = [
                'uid', 'doi', 'issn', 'eissn', 'pmid', 'authors', 'title', 'types',
                'sourceTitle', 'volume', 'issue', 'publishMonth', 'publishYear', 'citations',
                'keywords', 'record', 'citingArticles', 'references', 'related'
            ]
        writer.writerow(fieldnames)

# Initialise API caller
api_key = 'db9a7cce984907c62edd05528d3de1ab87af6159'        # Journal API
host = "https://api.clarivate.com/apis/wos-starter/v1"
wos_extractor = starter_API_getter.WoSDataExtractor(api_key, host)

# Open the CSV file for reading and make API calls in WoS
with open(core_file, mode='r', encoding='utf-8') as file:
    # Create a CSV reader object
    csv_reader = csv.reader(file)

    # Read the CSV header row
    headers = next(csv_reader)

    # Process each line in the CSV file
    for row in csv_reader:
        # Extract information based on the CSV headings
        journal_title = row[0]
        issn = row[1]
        eissn = row[2]
        published_by = row[3].lower()

        for publisher in publishers:
            timeout = 30
            time_elapsed = time.time() - start_time
            if time_elapsed >= timeout:
                for key, value in wos_extractor.counter.items():
                    print(f'{key}: {value}')
                print(f"Time elapsed: {time_elapsed: .2f} seconds.")
                print(f"Average: {wos_extractor.counter['total']/time_elapsed: .2f} papers per second.")
                exit()

            if type(publisher) is not list:
                if publisher in published_by:
                    wos_extractor.api_caller(journal_title, issn, eissn, publisher)
            else:
                if (publisher[0] and publisher[1]) in published_by:
                    wos_extractor.api_caller(journal_title, issn, eissn, 'tandf')
