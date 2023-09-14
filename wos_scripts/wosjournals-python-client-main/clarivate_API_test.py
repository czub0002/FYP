import csv
from pprint import pprint

import clarivate.wos_journals.client
from clarivate.wos_journals.client.api import journals_api

# https://github.com/clarivate/wosjournals-python-client


class WoSDataExtractor:
    def __init__(self, api_key, host):
        self.api_key = api_key
        self.configuration = clarivate.wos_journals.client.Configuration(
            host=host
        )

    def api_caller(self, journal_title, issn, eissn, publisher):
        # Enter a context with an instance of the API client
        with clarivate.wos_journals.client.ApiClient(self.configuration) as api_client:
            # Set the API key in the headers
            api_client.default_headers['X-ApiKey'] = self.api_key

            # Create an instance of the API class
            api_instance = journals_api.JournalsApi(api_client)

            # Create the query string based on whether ISSN and EISSN are available
            # if issn and eissn:
                # query = f"{issn} OR IS={eissn}"
            # TODO - fix
            if issn:
                query = issn
            elif eissn:
                query = eissn
            elif journal_title:
                query = journal_title.lower()
            else:
                print("ISSN, eISSN, and Journal Title are None")

            print(query)

            try:
                # Query Web of Science documents
                api_response = api_instance.journals_get(
                    q=query,
                    limit=1,
                    page=1,
                )

                pprint(api_response)

                # Iterate over the 'hits' in the API response body
                # TODO reject if specific data is missing (i.e. dois)
                # TODO refine what data is taken

                for hit in api_response.body['hits']:
                    fields_to_extract = ['uid', 'title', 'doi', 'issn', 'eissn']

                    # Create an empty dictionary to hold the extracted data
                    result = {}

                    # Extract data and populate the result dictionary
                    for field in fields_to_extract:
                        try:
                            if field == 'doi':
                                result[field] = hit['identifiers'][field]
                            else:
                                result[field] = hit[field]
                        except (KeyError, TypeError):
                            result[field] = 'none'

                    # Create an instance of the DataWoS class with the extracted data
                    data_wos_instance = DataWoS(
                        uid=result['uid'],
                        title=result['title'],
                        doi=result['doi'],
                        issn=result['issn'],
                        eissn=result['eissn'],
                        publisher=publisher  # Replace with the actual publisher name
                    )

                # TODO - make call to relevent csv file to write to
                # Make write once per query

            except clarivate.wos_journals.client.ApiException as e:
                print("Exception when calling DocumentsApi->documents_get: %s\n" % e)


class DataWoS:
    def __init__(self, uid, title, doi, issn, eissn, publisher):
        """
        Scrapes data from an HTML script on each listed article
        :param html_content: the webpage scraping the data from
        """
        self.uid = uid
        self.title = title
        self.doi = doi
        self.issn = issn
        self.eissn = eissn

        data = {
            "uid": self.uid,
            "title": self.title,
            "doi": self.doi,
            "issn": self.issn,
            "eissn": self.eissn,
        }

        print(data)

        publisher += '.csv'
        self.add_to_csv(data, publisher)

    def add_to_csv(self, data, file_path):
        """
        Writes data to a csv file
        :param data: article data being written to the csv file
        :param file_path: the path where the csv file is stored
        """
        # Open the CSV file with write permission
        with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
            # Create a CSV writer using the field/column names
            writer = csv.DictWriter(csvfile, fieldnames=data.keys())
            writer.writerow(data)