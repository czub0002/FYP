"""
Script interacts with Web Of Science API to retrieve information
"""
import csv

import clarivate.wos_starter.client
from clarivate.wos_starter.client.apis.tags import documents_api

# api_key = 'd8563637cb760fd52eb2d1dde0293b6e24752e74'
# "https://api.clarivate.com/apis/wos-starter/v1"


class WoSDataExtractor:
    def __init__(self, api_key, host):
        self.api_key = api_key
        self.configuration = clarivate.wos_starter.client.Configuration(
            host=host
        )

        self.counter = {
            'total': 0,
            'tandf': 0,
            'wiley': 0,
            'elsevier': 0,
            'springer': 0
        }

    def api_caller(self, issn, eissn, journal_title, publisher):
        # Enter a context with an instance of the API client
        with clarivate.wos_starter.client.ApiClient(self.configuration) as api_client:
            # Set the API key in the headers
            api_client.default_headers['X-ApiKey'] = self.api_key

            # Create an instance of the API class
            api_instance = documents_api.DocumentsApi(api_client)

            # Create the query string based on whether ISSN and EISSN are available
            if issn and eissn:
                query = f"IS=({issn} OR {eissn})"
            elif issn:
                query = f"IS={issn}"
            elif eissn:
                query = f"IS={eissn}"
            elif journal_title:
                query = f"SO={journal_title.lower()}"
            else:
                print("ISSN, eISSN, and Journal Title are None")

            # example passing only optional values
            # TODO - change to get all hits when API token is better
            query_params = {
                'q': query,
                # 'limit': 1,
                # 'page': 1,
            }

            try:
                # Query Web of Science documents
                api_response = api_instance.documents_get(
                    query_params=query_params,
                )

                # Iterate over the 'hits' in the API response body
                data_obj = []

                for hit in api_response.body['hits']:
                    self.counter['total'] += 1
                    self.counter[publisher] += 1

                    # pprint(hit)
                    fields_to_extract = ['uid', 'doi', 'issn', 'eissn', 'pmid',
                                         'authors', 'title', 'types',
                                         'sourceTitle', 'volume', 'issue', 'publishMonth', 'publishYear',
                                         'citations',
                                         'keywords',
                                         'record', 'citingArticles', 'references', 'related']

                    # Create an empty dictionary to hold the extracted data
                    result = {}

                    # Extract data and populate the result dictionary
                    for field in fields_to_extract:
                        try:
                            if field in ('doi', 'issn', 'eissn', 'pmid'):
                                result[field] = hit['identifiers'][field]
                            elif field == 'authors':
                                result[field] = []
                                for author in range(len(hit['names'][field])):
                                    author_name = tuple(hit['names'][field][author]['wosStandard'].split(','))
                                    result[field].append(author_name)
                            elif field in ('sourceTitle', 'volume', 'issue', 'publishMonth', 'publishYear'):
                                if field == 'publishYear':
                                    result[field] = hit['source'][field].as_int_oapg
                                else:
                                    result[field] = hit['source'][field]
                            elif field == 'citations':
                                result[field] = hit[field][0]['count'].as_int_oapg
                            elif field == 'keywords':
                                result[field] = hit[field]['authorKeywords']
                            elif field in ('record', 'citingArticles', 'references', 'related'):
                                result[field] = hit['links'][field]
                            else:
                                result[field] = hit[field]
                        except (KeyError, TypeError, IndexError):
                            result[field] = None

                    # Create an instance of the DataWoS class with the extracted data
                    data_wos_instance = DataWoS(
                        uid=result['uid'],
                        doi=result['doi'],
                        issn=result['issn'],
                        eissn=result['eissn'],
                        pmid=result['pmid'],
                        authors=result['authors'],
                        title=result['title'],
                        types=result['types'],
                        sourceTitle=result['sourceTitle'],
                        volume=result['volume'],
                        issue=result['issue'],
                        publishMonth=result['publishMonth'],
                        publishYear=result['publishYear'],
                        citations=result['citations'],
                        keywords=result['keywords'],
                        record=result['record'],
                        citingArticles=result['citingArticles'],
                        references=result['references'],
                        related=result['related']
                    )

                    data_obj.append(data_wos_instance)

                publisher += '.csv'
                for data in data_obj:
                    self.add_to_csv(data, publisher)

            except clarivate.wos_starter.client.ApiException as e:
                print("Exception when calling DocumentsApi->documents_get: %s\n" % e)

    def add_to_csv(self, data, file_path):
        """
        Writes data to a csv file
        :param data: article data being written to the csv file
        :param file_path: the path where the csv file is stored
        """
        # Open the CSV file with write permission
        with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
            fieldnames = [
                'uid', 'doi', 'issn', 'eissn', 'pmid', 'authors', 'title', 'types',
                'sourceTitle', 'volume', 'issue', 'publishMonth', 'publishYear', 'citations',
                'keywords', 'record', 'citingArticles', 'references', 'related'
            ]
            # Create a CSV writer with the fieldnames (header is not rewritten)
            csv_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Write the data from the DataWoS instance to the CSV file
            csv_writer.writerow(data.to_dict())


class DataWoS:
    def __init__(self, uid, doi, issn, eissn, pmid, authors, title, types, sourceTitle, volume, issue, publishMonth,
                 publishYear, citations, keywords, record, citingArticles, references, related):
        self.uid = uid
        self.doi = doi
        self.issn = issn
        self.eissn = eissn
        self.pmid = pmid
        self.authors = authors
        self.title = title
        self.types = types
        self.sourceTitle = sourceTitle
        self.volume = volume
        self.issue = issue
        self.publishMonth = publishMonth
        self.publishYear = publishYear
        self.citations = citations
        self.keywords = keywords
        self.record = record
        self.citingArticles = citingArticles
        self.references = references
        self.related = related

    def to_dict(self):
        return {
            'uid': self.uid,
            'doi': self.doi,
            'issn': self.issn,
            'eissn': self.eissn,
            'pmid': self.pmid,
            'authors': str(self.authors),
            'title': self.title,
            'types': ', '.join(self.types),
            'sourceTitle': self.sourceTitle,
            'volume': self.volume,
            'issue': self.issue,
            'publishMonth': self.publishMonth,
            'publishYear': self.publishYear,
            'citations': self.citations,
            'keywords': str(self.keywords),
            'record': self.record,
            'citingArticles': self.citingArticles,
            'references': self.references,
            'related': self.related
        }
