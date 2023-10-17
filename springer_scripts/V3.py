#Reading the HTML
import urllib.request
import csv

import cloudscraper
import pandas as pd 
import re

excel_file = 'Springer-Nature.xlsx'
df = pd.read_excel(excel_file)
doi_array = df['DOI'].tolist()
doi_link_arr = df['DOI Link'].tolist()
column_headings = ["Paper Title", "Journal Title", "Date", "Paper Type", "Volume", "Edition", "DOI", "WoS DOI", "Pages", "Authors", "Citations"]
cloud_scraper = cloudscraper.create_scraper()

# Creating a csv file to write the data into
with open('Article_Title_V3.csv', "a", newline='', encoding='utf-8') as csvfile:
    csv_writer = csv.writer(csvfile, delimiter=',')
    csv_writer.writerow(column_headings) 

    # looping for the DOIs to find
    for i in range(len(doi_link_arr)):
        doi_link = doi_link_arr[i]
        # url = "http://dx.doi.org/" + doi
        url = doi_link
        try: 
            # response = urllib.request.urlopen(url)
            response = cloud_scraper.get(doi_link)
            journal_contents = response.text
            # journal_contents = response.read().decode("utf-8")

        except cloudscraper.exceptions.CloudflareException as e:
            print(f"DOI Link {doi_link}:\nCloudflareException: {e}")
        except AttributeError as e:
            print(f"DOI Link {doi_link}:\nAttributeError: {e}")

        # except urllib.error.HTTPError as e:
        #     if e.code == 404:
        #         print(f"Article with DOI Link {doi_link} not found.")
        #     else:
        #         print(f"An error occurred for DOI Link {doi_link}: {str(e)}")

        if 400 <= response.status_code < '500':
            print(f"Article with DOI Link {doi_link} encountered status error: {response.status_code}.")

        # initialising variables for web-scraping
        strings_to_find = ['"og:title" content="', 'dc.source" content="', 'dc.date" content="', '"dc.type" content="',
                           '"prism.volume" content="', '"prism.number" content="', '"DOI" content="', '[WoS DOI]',
                           'citation_firstpage" content="', 'citation_lastpage" content="']
        author_string = 'dc.creator" content="'
        citation_string = 'citation_reference" content="'
        string_list = [] 
        authors = [] 
        citation_info_list = []

        pattern = re.compile(rf"{citation_string}([^\";]+)")
        citation_matches = pattern.finditer(journal_contents)
        
        for string in strings_to_find:
            if string == '[WoS DOI]':
                string_list.append(doi_array[i])
            else:
                start_index = 0
                while True:
                    index = journal_contents.find(string, start_index)
                    if index == -1:
                        break
                    end_index = journal_contents.find('"', index + len(string) + 1)
                    if end_index != -1:
                        value = journal_contents[index + len(string):end_index]
                        string_list.append(value)
                    start_index = end_index + 1

        author_index = 0
        while True:
            index = journal_contents.find(author_string, author_index)
            if index == -1:
                break
            end_index = journal_contents.find('"', index + len(author_string) + 1)
            if end_index != -1:
                value = journal_contents[index + len(author_string):end_index]
                authors.append(value)
            author_index = end_index + 1

        citation_index = 0
        while True:
            index = journal_contents.find(citation_string, citation_index)
            if index == -1:
                break
            citation_end_index = journal_contents.find('"', index + len(citation_string) + 1)
            if citation_end_index != -1:
                citation_content = journal_contents[index + len(citation_string):citation_end_index]
                # Split the citation content into key-value pairs
                pairs = citation_content.split('; ')
                citation_info = {}
                full_citation = None  # Initialize full_citation as None
                for pair in pairs:
                    parts = pair.split('=')
                    if len(parts) == 2:
                        key, value = parts
                        citation_info[key] = value
                    else:
                        # If the pair doesn't match the key-value pattern, store it as full_citation
                        full_citation = pair

                # If full_citation is not None, store it in citation_info
                if full_citation is not None:
                    citation_info["FullCitation"] = full_citation

                citation_info_list.append(citation_info)
                citation_index = citation_end_index + 1

        # Writing the extracted information into the CSV file created
        if len(string_list) >= len(strings_to_find) and len(authors) > 0 and len(citation_info_list) > 0:
            csv_writer.writerow([
                string_list[0], string_list[1], string_list[2], string_list[3],
                string_list[4], string_list[5], string_list[6], string_list[7],
                "Pages " + string_list[8] + ' to ' + string_list[9],
                ', '.join(authors), citation_info_list  
            ])
