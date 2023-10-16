import json
import time
from html import unescape
from urllib.parse import unquote

import requests
from bs4 import BeautifulSoup
import cloudscraper
from dateutil import parser
import csv
import re
import pandas as pd


class DataScraper:
    def __init__(self, scraper):
        """
        Scrapes data from an HTML script on each listed article
        :param scraper: webdriver used for webscraping = cloudscraper.create_scraper().get(url)
        """
        self.scraper = scraper
        source_content = scraper.text

        self.data_dict = None

        self.html_content = BeautifulSoup(source_content, 'html.parser')
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
            "doi": self.doi,
            "type": self.type,
            "title": self.title,
            "authors": self.authors,
            "received_date": self.dates.received_date,
            "revised_date": self.dates.revised_date,
            "accepted_date": self.dates.accepted_date,
            "published_date": self.dates.published_date,
            "version_date": self.dates.version_date,
            "journal": self.journal,
            "journal_edition": self.journal_edition,
            "url": self.url,
            "references": self.references
        }

        self.add_to_csv(data, 'elsevier_database.csv')

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
        doi_element = self.html_content.select_one('.doi')
        if doi_element:
            doi_url = self.string_cleaner(doi_element.get_text())

            url_prefix = "https://doi.org/"
            doi = doi_url[len(url_prefix):]
            print(f"doi: {doi}")
        else:
            print('DOI: Not Found')
            doi = None

        return doi

    def get_type(self):
        """
        Gets the type of article
        :return: String describing the paper type
        """
        article_heading_element = self.html_content.select_one('.article-dochead')
        if article_heading_element:
            article_type = self.string_cleaner(article_heading_element.get_text())
        else:
            print('Type: Not Found')
            article_type = None

        return article_type

    def get_title(self):
        """
        Gets the title of the paper
        :return: string containing paper title
        """
        title_element = self.html_content.select_one('.article-dochead')
        if not title_element:
            title_element = self.html_content.select_one('.title-text')

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
        author_container = self.html_content.select_one('.author-group')

        # Searches and extracts each listed author
        if author_container:
            author_elements = author_container.find_all('span', class_='react-xocs-alternative-link')
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
        # Initialise variables
        dates = {
            "Received": None,
            "Revised": None,
            "Publication date": None,
            "Available online": None,
            "Version of Record": None
        }

        try:
            json_container = self.html_content.find('script', attrs={'type': 'application/json'}).text
            self.data_dict = json.loads(json_container)

            # Initialize variables to store the dates
            # Find the div containing the date information
            paper_dates = self.data_dict['article']['dates']

            for key, date in paper_dates.items():
                if type(date) is not list:
                    dates[key] = parser.parse(date, fuzzy=True).date()
                else:
                    for i in range(len(date)):
                        date[i] = parser.parse(date[i], fuzzy=True).date()
        except KeyError as e:
            # Handle the case where the 'dates' key is not found in the dictionary
            print(f"KeyError: {e}. 'dates' key not found in the JSON data.")
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            print(f"JSONDecodeError: {e}. There was an error decoding JSON data.")
        except Exception as e:
            # Handle other exceptions that may occur
            print(f"An error occurred: {e}")

        return Dates(dates["Received"], dates["Revised"], dates["Publication date"],
                     dates["Available online"], dates["Version of Record"])

    def get_journal(self):
        """
        Gets the journal name
        :return: string containing journal name
        """
        journal_element = self.html_content.select_one('.publication-title')
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
        journal_ed_element = self.html_content.select_one('.publication-volume')
        journal_ed_element = journal_ed_element.select_one('div', class_='text-xs')

        if journal_ed_element:
            journal_ed = self.string_cleaner(journal_ed_element.get_text())
        else:
            print("Journal Edition: Not Found")
            journal_ed = None

        return journal_ed

    def get_url(self):
        """
        Gets the url of the paper
        :return: string containing the url to access the paper
        """
        # initialise url variable
        url = None

        try:
            url = self.scraper.url
        except self.scraper.exceptions.RequestException as e:
            print("RequestException:", e)
        except cloudscraper.exceptions.CloudflareException as e:
            print("CloudflareException:", e)
        except AttributeError as e:
            print("AttributeError:", e)

        return url

    def get_references(self):
        """
        Gets a list of all the references listed in the paper
        :return: a list, with each item in the list being a reference cited by the authors
        """
        ref_list = []

        try:
            if self.data_dict:
                references = self.data_dict["references"]["sourceTextMap"]
            else:
                return ref_list
        except KeyError:
            print("References not found!")
            return ref_list

        for ref in references.values():
            ref_list.append(ref)

        return ref_list

    def string_cleaner(self, text):
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        return cleaned_text


class Dates:
    def __init__(self, received_date, revised_date, accepted_date, published_date, version_date):
        """
        Class stores all the dates in their own Dates object
        :param received_date: the date which the paper was received
        :param accepted_date: the date which the paper was accepted
        :param published_date: the date which the paper was published
        """
        self.received_date = received_date
        self.revised_date = revised_date
        self.accepted_date = accepted_date
        self.published_date = published_date
        self.version_date = version_date


def main():
    big_start = time.time()

    fields = ['doi', 'type', 'title', 'authors', 'received_date', 'revised_date', 'accepted_date', 'published_date',
              'version_date', 'journal', 'journal_edition', 'url', 'references']
    file_path = 'elsevier_database.csv'

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer using the field/column names
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

    # url = 'https://www.sciencedirect.com/science/article/pii/S0022169423009253#ab005'

    df = pd.read_excel('Elsevier.xlsx')
    counter = 0
    cloud_scraper = cloudscraper.create_scraper()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    }

    if 'DOI Link' in df.columns:
        for index, row in df.iterrows():
            counter += 1
            print(str(counter) + ' ------------------')

            # Stops at 50, remove later
            if counter == 50:
                break

            doi_link_value = row["DOI Link"]

            if doi_link_value:
                # First response is the html landing page which is NOT the page
                response = requests.get(doi_link_value)

                soup = BeautifulSoup(response.text, 'html.parser')
                redirect_url = soup.find(name="input", attrs={"name": "redirectURL"})["value"]
                final_url = unescape(unquote(redirect_url))
                response = requests.get(final_url, headers=headers)

                # This code finds where the landing page tries to redirect to (JavaScript)
                if response.status_code == 200:
                    DataScraper(response)

                else:
                    print(f"ERROR: Status {response.status_code}")

    big_end = time.time()
    total_time = big_end - big_start
    print(f"Total Time: {total_time:.4f}")


if __name__ == '__main__':
    main()
