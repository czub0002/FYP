import math
import time
from bs4 import BeautifulSoup
import cloudscraper
from dateutil import parser
import csv
import re
import pandas as pd
from time import strftime, localtime
import tabulate
from pathlib import Path
from selenium import webdriver


class DataScraper:
    def __init__(self, scraper, wos_doi):
        """
        Scrapes data from an HTML script on each listed article
        :param scraper: webdriver used for webscraping = cloudscraper.create_scraper().get(url)
        :param wos_doi: DOI listed in the Web of Science database
        """
        self.scraper = scraper
        source_content = scraper.page_source

        self.html_content = BeautifulSoup(source_content, 'html.parser')

        self.wos_doi = wos_doi
        self.doi = self.get_doi()
        self.type = self.get_type()
        self.title = self.get_title()
        self.authors = self.get_authors()
        self.dates = self.get_dates()
        self.journal = self.get_journal()
        self.journal_edition = self.get_journal_edition()
        self.url = self.get_url()
        self.references = self.get_references()

        data = {
            "wos_doi": self.wos_doi,
            "doi": self.doi,
            "type": self.type,
            "title": self.title,
            "authors": self.authors,
            "received_date": self.dates.received_date,
            "accepted_date": self.dates.accepted_date,
            "published_date": self.dates.published_date,
            "journal": self.journal,
            "journal_edition": self.journal_edition["journal_ed"],
            "publication_year": self.journal_edition["pub_year"],
            "uid": self.journal_edition["uid"],
            "issue": self.journal_edition["issue"],
            "url": self.url,
            "references": self.references
        }

        self.add_to_csv(data, 'wiley_database.csv')

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

    def get_doi(self):
        """
        Extracts the DOIs of the paper
        :return: DOI of the article
        """
        doi_element = self.html_content.select_one('.epub-doi')
        if doi_element:
            doi_url = self.string_cleaner(doi_element.get_text())

            url_prefix = "https://doi.org/"
            doi = doi_url[len(url_prefix):]

            print(doi)
        else:
            print('DOI: Not Found')
            doi = None

        return doi

    def get_type(self):
        """
        Gets the type of article
        :return: String describing the paper type
        """
        article_heading_element = self.html_content.select_one('.doi-access-container')
        type_element = article_heading_element.find('span', class_='primary-heading')

        if type_element:
            article_type = self.string_cleaner(type_element.get_text())
        else:
            print('Type: Not Found')
            article_type = None

        return article_type

    def get_title(self):
        """
        Gets the title of the paper
        :return: string containing paper title
        """
        title_element = self.html_content.select_one('.citation__title')

        if title_element:
            title = self.string_cleaner(title_element.get_text())
        else:
            print('Title: Not Found')
            title = None

        return title

    def get_authors(self):
        """
        Retrieves a list of the authors for each paper
        :return: List of authors
        """
        author_list = []
        author_container = self.html_content.select_one('.loa-authors')

        # Searches and extracts each listed author
        if author_container:
            author_elements = author_container.find_all('a', class_='author-name')
            # Adding each author to a list
            for author_element in author_elements:
                author_name = self.string_cleaner(author_element.get_text())
                author_list.append(author_name)
        else:
            print('Authors: Not Found')
            author_list = None

        return author_list

    def get_dates(self):
        """
        Searches for Received, Accepted and Published dates of the paper
        :return: Date object containing Received, Accepted and Published dates
        """
        # Initialize variables to store the dates
        received_date = None
        accepted_date = None
        published_date = None

        published_date_container = self.html_content.select_one('.epub-date')

        if not published_date_container:
            print("Dates: Not Found")
            return None

        try:
            date_str = self.string_cleaner(published_date_container.get_text())
            published_date = parser.parse(date_str, fuzzy=True).date()
        except ValueError:
            print("Received Date: Parsing Error")

        return Dates(received_date, accepted_date, published_date)

    def get_journal(self):
        """
        Gets the journal name
        :return: string containing journal name
        """
        journal_element = self.html_content.select_one('.journal-banner-text')
        if journal_element:
            journal_title = self.string_cleaner(journal_element.get_text())
        else:
            print("Journal Title: Not Found")
            journal_title = None

        return journal_title

    def get_journal_edition(self):
        """
        Gets the journal edition
        :return: string containing journal name
        """
        journal_edition = {'journal_ed': None, 'uid': None, 'issue': None, 'pub_year': None}

        journal_ed_element = self.html_content.select_one('.volume-issue')
        if journal_ed_element:
            journal_ed = self.string_cleaner(journal_ed_element.get_text())

            # Define a regular expression pattern to match numbers
            pattern = r'\d+'

            # Use re.findall to extract all numbers from the string
            matches = re.findall(pattern, journal_ed, re.IGNORECASE)

            # Extract information from the matches
            # Assuming you want the first number to be the 'uid' and the second to be the 'issue'
            journal_edition["uid"] = int(matches[0]) if matches else None
            journal_edition["issue"] = int(matches[1]) if len(matches) > 1 else None

            # Get publication year
            pub_year_element = self.html_content.select('.extra-info-wrapper p')[1]

            if pub_year_element:
                try:
                    pub_year = self.string_cleaner(pub_year_element.get_text())
                    extracted_date = parser.parse(pub_year, fuzzy=True)
                    pub_year = extracted_date.date().year
                except ValueError:
                    pub_year = None
            else:
                print("Journal Edition: Not Found")
                pub_year = None

            journal_edition['pub_year'] = pub_year
        else:
            print("Journal Edition: Not Found")
            journal_ed = None

        journal_edition['journal_ed'] = journal_ed

        return journal_edition

    def get_url(self):
        """
        Gets the url of the paper
        :return: string containing the url to access the paper
        """
        # initialise url variable
        url = None

        try:
            url = self.scraper.current_url
        except AttributeError as e:
            print("AttributeError:", e)

        return url

    def get_references(self):
        """
        Gets a list of all the references listed in the paper
        :return: a list, with each item in the list being a reference cited by the authors
        """
        ref_list = []
        references_container = self.html_content.select_one('.article-section__references')

        if references_container:
            reference_elements = references_container.find_all('li')
            for reference_element in reference_elements:
                ref = self.string_cleaner(reference_element.get_text())
                ref_list.append(ref)
        else:
            print("References: Not Found")
            ref_list = None

        return ref_list

    def string_cleaner(self, text):
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return cleaned_text


class Dates:
    def __init__(self, received_date, accepted_date, published_date):
        """
        Class stores all the dates in their own Dates object
        :param received_date: the date which the paper was received
        :param accepted_date: the date which the paper was accepted
        :param published_date: the date which the paper was published
        """
        self.received_date = received_date
        self.accepted_date = accepted_date
        self.published_date = published_date


def main():
    start_time = time.time()
    summary_of_errors = "______________________________________________________\n" \
                        "-------------- Summary of Status Errors --------------\n"
    termination_statement = 'SUCCESS: Script ran until completion!'

    fields = ['wos_doi', 'doi', 'type', 'title', 'authors', 'received_date', 'accepted_date', 'published_date',
              'journal', 'journal_edition', 'publication_year', 'uid', 'issue', 'url', 'references']
    file_path = 'wiley_database.csv'
    start_index = 0
    path = Path(file_path)
    df = pd.read_excel('Wiley.xlsx')

    if not path.is_file():
        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            # Create a CSV writer using the field/column names
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
    else:
        wiley_df = pd.read_csv(file_path)

        if not wiley_df.empty:
            last_doi = wiley_df.iloc[-1]["wos_doi"]
            matching_rows = df[df["DOI"] == last_doi]
            start_index = matching_rows.index[-1] + 1

    # TODO - Proxy/user agent rotation
    browser = webdriver.Chrome()
    counter = 0

    # keep record of status errors
    status_errors = []
    previous_identifier = (None, None, None)  # (ISSN, eISSN, ISBN)

    for index, row in df.iloc[start_index:].iterrows():
        counter += 1

        print(f"{counter} -----------------------------")

        # TODO - Check DOI always exists when DOI Link does in WoS database before executing script
        doi_link_value = row["DOI Link"]
        wos_doi = row["DOI"]

        has_url = False

        try:
            if math.isnan(doi_link_value):
                print("Paper has no URL!")
        except TypeError:
            has_url = True

        if has_url:
            browser.delete_all_cookies()
            browser.get(doi_link_value)
            response_url = browser.current_url

            if "epdf" in response_url:
                modified_url = response_url.replace("/epdf/", "/abs/")
                browser.get(modified_url)
            else:
                modified_url = response_url.replace("/doi/", "/doi/abs/")
                browser.delete_all_cookies()
                browser.get(modified_url)

            DataScraper(browser, wos_doi)

    end_time = time.time()
    total_time = end_time - start_time

    m, s = divmod(total_time, 60)
    h, m = divmod(m, 60)
    total_runtime = f'Total Runtime: {h:0.0f} hours, {m:0.0f} minutes, {s:02.2f} seconds.'

    # Structure summary of errors output
    header = ["Status Code", "Index", "DOI"]
    error_list = []
    for error in status_errors:
        error_list.append([error["status_code"], error["index"], error["data"]["DOI"]])

    error_table = tabulate.tabulate(error_list, header)
    summary_of_errors += error_table
    total_errors = f"Total Status Errors: {str(len(error_list))}"

    lines = ['\n',
             strftime('Start Time: %H:%M:%S\t%d/%m/%Y\n', localtime(start_time)),
             strftime('End Time: %H:%M:%S\t%d/%m/%Y\n', localtime(end_time)),
             total_runtime + '\n',
             'Papers: ' + str(counter) + '\n',
             summary_of_errors + '\n\n',
             total_errors + '\n\n\n',
             termination_statement + '\n\n\n\n'
             ]

    # Summary of Execution Log
    with open('wiley_execution_log.txt', "a", encoding="utf-8") as txtfile:
        """
        Start Time:
        End Time:
        Total Runtime:
        Papers:
        Summary of Status Errors
        Total Status Errors:
        Termination Statement:

        """
        for line in lines:
            print(line)
            txtfile.write(line)


if __name__ == '__main__':
    main()
