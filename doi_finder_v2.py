from selenium import webdriver
from dateutil import parser
import html
import re


class DataScraper:
    def __init__(self, html_content):
        """
        Scrapes data from a HTML script on each listed article
        :param html_content: the webpage scraping the data from
        """
        self.html_content = html_content
        self.data = self.find_doi()

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

            # Checks for duplicate doi
            if doi not in doi_list:
                doi_info = ArticleInfo(self.html_content, doi)
                doi_list.append(doi_info)

        return doi_list


class ArticleInfo:
    def __init__(self, html_content, doi):
        """
        Extracts all the relevant data from each article
        :param html_content: the webpage html
        :param doi: the doi of each article
        """
        self.html_content = html_content
        self.doi = doi

        self.doi_index = html_content.find(self.doi)

        self.title = self.get_title()
        self.authors = self.get_authors()
        self.pubdate = self.get_pubdate()
        self.journal = self.get_journal()

    def get_title(self):
        """
        Gets the title of the journal
        :return: string containing journal title
        """
        title_query = "hlFld-Title"
        title_index = self.html_content.find(title_query, self.doi_index)

        # searches for start and end indexes of the title
        start_of_title = self.html_content.find(">", title_index) + 1
        end_of_title = self.html_content.find("</span>", start_of_title)

        # cleans string if it contains html tags
        title = self.string_cleaner(self.html_content[start_of_title:end_of_title])

        return title

    def get_authors(self):
        """
        Retrieves a list of the authors for each paper
        :return: List of authors
        """
        author_list = []
        last_author = False
        doi_index = self.doi_index

        # Loops until it has found each author
        while not last_author:
            author_query = "/author/"
            author_index = self.html_content.find(author_query, doi_index)

            # searches for start and end indexes of the author name
            start_of_name = self.html_content.find(">", author_index) + 1
            end_name_index = self.html_content.find("</a>", start_of_name)

            # cleans string if it contains html tags
            author = self.string_cleaner(self.html_content[start_of_name:end_name_index])
            author_list.append(author)

            # updates starting search position so same author is not found each time
            doi_index = end_name_index

            # check if final author name
            last_author_query = '</a></span></span>'
            if self.html_content[end_name_index:end_name_index + len(last_author_query)] == last_author_query:
                last_author = True

        return author_list

    def get_pubdate(self):
        """
        Gets the date the paper was published
        :return: date object of the published date
        """
        pubdate_query = "tocEPubDate"
        pubdate_div = self.html_content.find(pubdate_query, self.doi_index)

        # searches for start and end indexes of the title
        start_of_div = self.html_content.find("date", pubdate_div)
        end_of_div = self.html_content.find("</div>", start_of_div)

        input_string = self.html_content[start_of_div:end_of_div]

        try:
            extracted_date = parser.parse(input_string, fuzzy=True)
            pubdate = extracted_date.date()
        except ValueError:
            pubdate = "Not Found"

        return pubdate

    def get_journal(self):
        """
        Gets the journal name
        :return: string containing journal name
        """
        # searches for start and end indexes of the title
        start_of_title = self.html_content.find("<title>") + len("<title>")
        end_of_title = self.html_content.find("</title>")

        # cleans string if it contains html tags
        journal_title = self.string_cleaner(self.html_content[start_of_title:end_of_title])

        return journal_title

    def string_cleaner(self, original_string):
        """
        Cleans string if it contains html tags
        :param original_string: string to be cleaned
        :return: original string with no html tags
        """
        decoded_string = html.unescape(original_string)
        cleaned_string = re.sub(r'<.*?>', '', decoded_string)

        return cleaned_string


def main():
    url = 'https://www.tandfonline.com/toc/twas20/36/1?nav=tocList'
    # url = 'https://www.tandfonline.com/toc/rabf21/33/1?nav=tocList'

    # start WebDriver
    browser = webdriver.Chrome()
    browser.get(url)
    html_content = browser.page_source

    info = DataScraper(html_content)

    print("No. of unique DOIs: " + str(len(info.data)) + '\n')

    for article in info.data:
        print('Doi: ' + article.doi + '\n' +
              'Title: ' + article.title + '\n' +
              'Authors: ' + str(article.authors) + '\n' +
              'Published Date: ' + str(article.pubdate) + '\n' +
              'Journal: ' + article.journal + '\n\n')


if __name__ == '__main__':
    main()
