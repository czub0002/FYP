import time
import clarivate.wos_journals.client
from clarivate.wos_journals.client.api import journals_api
from clarivate.wos_journals.client.model.journal_list import JournalList
from pprint import pprint
# Defining the host is optional and defaults to https://api.clarivate.com/apis/wos-journals/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = clarivate.wos_journals.client.Configuration(
    host = "https://api.clarivate.com/apis/wos-journals/v1"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure API key authorization: key
configuration.api_key['key'] = 'f66216af8455914dcee7e062b8a427f325e99f8d'

# Uncomment below to setup prefix (e.g. Bearer) for API key, if needed
# configuration.api_key_prefix['key'] = 'Bearer'

# Enter a context with an instance of the API client
with clarivate.wos_journals.client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = journals_api.JournalsApi(api_client)
    q = "0945-053X" # str | Free-text search by journal name (e.g. *Nature Genetics*), JCR abbreviation (e.g. *NAT GENET*), publisher (e.g. *PUBLIC LIBRARY SCIENCE*) or [ISSN / eISSN code](https://www.issn.org/understanding-the-issn/what-is-an-issn/) (e.g. *1061-4036*)  The search logic is described in the section [Search](#search). (optional)
    page = 1 # int | Specifying a page to retrieve (optional) if omitted the server will use the default value of 1
    limit = 10 # int | Number of returned results, ranging from 0 to 50 (optional) if omitted the server will use the default value of 10

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # Search and filter across JCR Journals
        api_response = api_instance.journals_get(q=q, page=page, limit=limit)
        # pprint(api_response)
    except clarivate.wos_journals.client.ApiException as e:
        print("Exception when calling JournalsApi->journals_get: %s\n" % e)

    # Access the 'received_data' attribute in the response
    journals = api_response['hits']

    # Iterate through the list of journals and extract relevant information
    for journal in journals:
        journal_id = journal['id']
        journal_name = journal['name']
        issn = journal['matches'][0]['value'][0]  # Extract the ISSN from the first match

        print("Journal ID:", journal_id)
        print("Journal Name:", journal_name)
        print("ISSN:", issn)
        print("-------------------------------------------------")

    # You can access other fields in the response as needed
