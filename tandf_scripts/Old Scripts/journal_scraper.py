import time
from bs4 import BeautifulSoup
import cloudscraper
import csv
import tandf_webscraper


class JournalScraper:
    def __init__(self, html_content, scraper):
        """
        Scrapes data from an HTML script on each listed article
        :param html_content: the webpage scraping the data from
        """
        self.html_content = html_content
        self.scraper = scraper
        self.find_doi()

    def find_doi(self):
        """
        Extracts the DOIs of each article in the journal
        :return: List of each DOI and its associated information
        """
        query = "doi/ref/"
        start_index = 0
        appearances = []
        doi_list = []

        # Find each instance of the query
        while True:
            index = self.html_content.find(query, start_index)
            if index == -1:
                break
            appearances.append(index)
            start_index = index + len(query)

        # Extracting the doi from the string
        for index in appearances:
            # searches for end index of the doi
            start_of_doi = index + len(query)
            end_of_doi = self.html_content.find("\"", start_of_doi)
            doi = self.html_content[start_of_doi:end_of_doi]

            paper_url = "https://www.tandfonline.com/doi/" + doi

            source_content = self.scraper.get(paper_url)

            # Checks for duplicate doi
            if doi not in doi_list:
                doi_info = tandf_webscraper.DataScraper(source_content)
                doi_list.append(doi_info)


def main():
    fields = ['doi', 'type', 'title', 'authors', 'received_date', 'accepted_date', 'published_date', 'journal',
              'journal_edition', 'url', 'references']
    file_path = 'tandf_database.csv'

    with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
        # Create a CSV writer using the field/column names
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer.writeheader()

    big_start = time.time()
    url = 'https://www.tandfonline.com/toc/twas20/36/1?nav=tocList'
    # url = 'https://www.tandfonline.com/toc/rabf21/33/1?nav=tocList'

    # start WebDriver
    scraper = cloudscraper.create_scraper()
    source_content = scraper.get(url).text

    JournalScraper(source_content, scraper)

    big_end = time.time()
    total_time = big_end - big_start
    print(f"Total Time: {total_time:.4f}")


if __name__ == '__main__':
    main()
