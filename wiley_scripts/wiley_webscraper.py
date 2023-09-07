import time
from bs4 import BeautifulSoup
import cloudscraper
from dateutil import parser
import csv
import re


class DataScraper:
    def __init__(self, html_content):
        """
        Scrapes data from an HTML script on each listed article
        :param html_content: the webpage scraping the data from
        """
        self.html_content = html_content
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
            "accepted_date": self.dates.accepted_date,
            "published_date": self.dates.published_date,
            "journal": self.journal,
            "journal_edition": self.journal_edition,
            "url": self.url,
            "references": self.references
        }

        print(data)

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
        date_container = self.html_content.select_one('.epub-date')

        if not date_container:
            print("Dates: Not Found")
            return None

        # Initialize variables to store the dates
        received_date = None
        accepted_date = None
        published_date = None

        try:
            date_str = self.string_cleaner(date_container.get_text())
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
        journal_ed_element = self.html_content.select_one('.volume-issue')
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
        if self.doi:
            url = "https://acsess.onlinelibrary.wiley.com/doi/" + self.doi
        else:
            print("url: Not Found - Missing DOI")
            url = None

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
    big_start = time.time()

    fields = ['doi', 'type', 'title', 'authors', 'received_date', 'accepted_date', 'published_date', 'journal',
              'journal_edition', 'url', 'references']
    file_path = 'wiley_database.csv'

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer using the field/column names
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

    url = 'https://acsess.onlinelibrary.wiley.com/doi/10.1002/crso.20301'

    # start WebDriver
    scraper = cloudscraper.create_scraper()
    source_content = scraper.get(url).text
    html_content = BeautifulSoup(source_content, 'html.parser')

    DataScraper(html_content)

    big_end = time.time()
    total_time = big_end - big_start
    print(f"Total Time: {total_time:.4f}")


if __name__ == '__main__':
    main()
