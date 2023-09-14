"""
Script runs through wos core journal lists and calls clarivate_API_test.py to perform WoS API requests to extract
the relevant data. This is then stored in a csv (depending on the publisher) to build the database.
"""

import csv
import clarivate_API_test

publishers = ["elsevier", "springer", ["taylor", "francis"], "wiley"]
# core_files = ["wos-core_SCIE 2023-August-22.csv", "wos-core_SSCI_2023-August-22.csv"]
core_file = "../wosstarter_python_client/wos-core_SCIE 2023-August-22.csv"

# Creating a csv for WOS database - one for each publisher
for publisher in publishers:
    if type(publisher) is list:
        publisher = 'tandf'
    with open(f"{publisher}.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)

        # Create header for WoS data
        # TODO - update after determining the data to pull
        writer.writerow(["uid", "title", "doi", "issn", "eissn"])

# Initialise API caller
api_key = 'f66216af8455914dcee7e062b8a427f325e99f8d'        # Journal API
host = "https://api.clarivate.com/apis/wos-journals/v1"
wos_extractor = clarivate_API_test.WoSDataExtractor(api_key)

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
            if type(publisher) is not list:
                if publisher in published_by:
                    wos_extractor.api_caller(journal_title, issn, eissn, publisher)
            else:
                if (publisher[0] and publisher[1]) in published_by:
                    wos_extractor.api_caller(journal_title, issn, eissn, 'tandf')
