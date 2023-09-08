import clarivate.wos_starter.client
from clarivate.wos_starter.client.apis.tags import documents_api

# Replace 'your-api-key' with your actual API key
api_key = 'd8563637cb760fd52eb2d1dde0293b6e24752e74'

# Defining the host is optional and defaults to http://api.clarivate.com/apis/wos-starter
# See configuration.py for a list of all supported configuration parameters.
configuration = clarivate.wos_starter.client.Configuration(
    host="https://api.clarivate.com/apis/wos-starter/v1"
)

# Enter a context with an instance of the API client
with clarivate.wos_starter.client.ApiClient(configuration) as api_client:
    # Set the API key in the headers
    api_client.default_headers['X-ApiKey'] = api_key

    # Create an instance of the API class
    api_instance = documents_api.DocumentsApi(api_client)

    # Identifiers
    issn = '0155-9982'
    eissn = '1467-6303'
    journal_title = 'ACCOUNTING FORUM'.lower()

    # Create the query string based on whether ISSN and EISSN are available
    if issn and eissn:
        query = f"IS=({issn} OR {eissn})"
    elif issn:
        query = f"IS={issn}"
    elif eissn:
        query = f"IS={eissn}"
    elif journal_title:
        query = f"SO={journal_title}"
    else:
        print("ISSN, eISSN, and Journal Title are None. Please provide at least one.")
        exit(1)

    # example passing only optional values
    query_params = {
        'q': query,
        'limit': 1,
        'page': 1,
    }

    try:
        # Query Web of Science documents
        api_response = api_instance.documents_get(
            query_params=query_params,
        )

        # Iterate over the 'hits' in the API response body
        for hit in api_response.body['hits']:
            uid = hit['uid']
            title = hit['title']
            doi = hit['identifiers']['doi']
            issn = hit['identifiers']['issn']
            eissn = hit['identifiers']['eissn']

            # Print the extracted information
            print(f"UID: {uid}")
            print(f"Title: {title}")
            print(f"DOI: {doi}")
            print(f"ISSN: {issn}")
            print(f"EISSN: {eissn}")
            print("")

    except clarivate.wos_starter.client.ApiException as e:
        print("Exception when calling DocumentsApi->documents_get: %s\n" % e)
