from bs4 import BeautifulSoup
from dateutil import parser
import html
import re
import cProfile
import time
from selenium import webdriver


class DataScraper:
    def __init__(self, html_content):
        """
        Scrapes data from a HTML script on each listed article
        :param html_content: the webpage scraping the data from
        """
        self.html_content = html_content
        self.browser = webdriver.Chrome()
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
                doi_info = ArticleInfo(self.html_content, doi, self.browser)
                doi_list.append(doi_info)

        return doi_list


class ArticleInfo:
    def __init__(self, html_content, doi, browser):
        """
        Extracts all the relevant data from each article
        :param html_content: the webpage html
        :param doi: the doi of each article
        """
        start_time = time.time()

        self.html_content = html_content
        self.soup = BeautifulSoup(self.html_content, 'html.parser')
        self.doi = doi

        self.doi_index = html_content.find(self.doi)

        start_ops = time.time()

        self.title = self.get_title()

        title_time = time.time()

        self.authors = self.get_authors()
        authors_time = time.time()
        self.journal = self.get_journal()
        journal_time = time.time()
        self.url = self.get_article_link()
        url_time = time.time()

        self.times = [start_time, start_ops, title_time, authors_time, journal_time, url_time]

        # Information from article webpage
        detailed_article = DetailedArticleInfo(self.url, browser)

        self.times += detailed_article.times
        time_names = ['start_time', 'start_ops', 'title_time', 'authors_time', 'journal_time', 'url_time',
                      'article_time', 'soup_time', 'type_time', 'ref_time', 'dates_time']

        self.type = detailed_article.type
        self.references = detailed_article.references
        self.dates = detailed_article.dates

        print(f"doi - {self.doi}")
        for i in range(len(self.times)-1):
            time_elapsed = self.times[i+1] - self.times[i]
            print(f"{time_names[i+1]}: {time_elapsed:.4f}")
        print('\n')

    def get_title(self):
        title_element = self.soup.select_one('.hlFld-Title')
        title = string_cleaner(title_element.get_text())
        return title

    def get_authors(self):
        """
        Retrieves a list of the authors for each paper
        :return: List of authors
        """
        author_list = []

        author_container = self.soup.select_one('.tocAuthors.afterTitle .articleEntryAuthorsLinks')
        if author_container:
            author_elements = author_container.find_all('a')
            for author_element in author_elements:
                author_name = string_cleaner(author_element.get_text())
                author_list.append(author_name)

        return author_list

    def get_journal(self):
        """
        Gets the journal name
        :return: string containing journal name
        """
        title_element = self.soup.select_one('title')
        if title_element:
            journal_title = string_cleaner(title_element.get_text())
        else:
            journal_title = "Journal title not found."

        return journal_title

    def get_article_link(self):
        """
        Gets link of each article
        :return: string of url for each article
        """
        # searches for start and end indexes of the article link
        start_of_href = self.html_content.find("href=\"", self.doi_index) + len("href=\"")
        end_of_href = self.html_content.find("\"", start_of_href)

        href = self.html_content[start_of_href:end_of_href]
        url = "https://www.tandfonline.com" + href

        return url


class DetailedArticleInfo:
    def __init__(self, article_url, browser):
        # self.doi = doi
        self.article = self.get_article(browser, article_url)
        article_time = time.time()

        self.soup = BeautifulSoup(self.article, 'html.parser')
        soup_time = time.time()

        self.type = self.get_article_type()
        type_time = time.time()

        self.references = self.get_references()
        ref_time = time.time()

        self.dates = self.get_dates()
        dates_time = time.time()

        self.times = [article_time, soup_time, type_time, ref_time, dates_time]

    def get_article(self, browser, article_url):
        '''
        # -----------------------------------------------------------------
        # TODO - Remove when web scraping
        with open('web_link.html', 'r', encoding='utf-8') as html_file:
            file = html_file.read()

        soup = BeautifulSoup(file, 'html.parser')
        article = soup.get_text()

        return article
        '''
        browser.delete_all_cookies()
        browser.get(article_url)

        html_content = browser.page_source

        return html_content
        # ------------------------------------------------------------------

    '''
    def get_title(self):
        soup = BeautifulSoup(self.article, 'html.parser')  # Create the BeautifulSoup object
        title_element = soup.select_one('.NLM_article-title.hlFld-Title')
        title = string_cleaner(title_element.get_text())
        return title
    '''

    def get_article_type(self):
        article_heading_element = self.soup.select_one('.toc-heading')
        if article_heading_element:
            article_type = article_heading_element.get_text()
        else:
            article_type = 'Type not found.'

        return article_type  # Return None if article heading element not found

    def get_references(self):
        ref_list = []
        references_container = self.soup.select_one('.references')
        if references_container:
            reference_elements = references_container.find_all('li')
            for reference_element in reference_elements:
                ref = string_cleaner(reference_element.get_text())
                ref_list.append(ref)

        return ref_list

    def get_dates(self):
        received_query = "Received"
        accepted_query = "Accepted"
        published_query = "Published online"

        rec_date = self.search_date_extractor(received_query)
        acc_date = self.search_date_extractor(accepted_query)
        pub_date = self.search_date_extractor(published_query)

        return Dates(rec_date, acc_date, pub_date)

    def search_date_extractor(self, query):
        end_query1, end_query2 = ",", "</div>"

        search_query = self.article.find(query)
        date_string1 = self.article[search_query:self.article.find(end_query1, search_query)]
        date_string2 = self.article[search_query:self.article.find(end_query2, search_query)]

        if date_string1 < date_string2:
            date_string = date_string1
        else:
            date_string = date_string2

        try:
            extracted_date = parser.parse(date_string, fuzzy=True)
            date = extracted_date.date()
        except ValueError:
            date = None

        return date


class Dates:
    def __init__(self, received_date, accepted_date, published_date):
        self.received_date = received_date
        self.accepted_date = accepted_date
        self.published_date = published_date


def string_cleaner(original_string):
    """
    Cleans string if it contains html tags
    :param original_string: string to be cleaned
    :return: original string with no html tags
    """
    decoded_string = html.unescape(original_string)
    cleaned_string = re.sub(r'<.*?>', '', decoded_string)

    return cleaned_string


def main():
    big_start = time.time()
    # Read the HTML file
    with open('webpage.html', 'r', encoding='utf-8') as html_file:
        source_content = html_file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(source_content, 'html.parser')

    # Extract text content from the parsed HTML
    html_file = soup.get_text()

    info = DataScraper(html_file)

    big_end = time.time()

    print(f"Total Time: {big_end-big_start:.4f}")

    # print("No. of unique DOIs: " + str(len(info.data)))

    '''
    for article in info.data:
        print('Doi: ' + article.doi + '\n' +
              'Type: ' + article.type + '\n' +
              'Title: ' + article.title + '\n' +
              'Authors: ' + str(article.authors) + '\n' +
              'Received Date: ' + str(article.dates.received_date) + '\n' +
              'Accepted Date: ' + str(article.dates.accepted_date) + '\n' +
              'Published Date: ' + str(article.dates.published_date) + '\n' +
              'Journal: ' + article.journal + '\n' +
              'url: ' + article.url + '\n' +
              'References: ' + str(article.references) + '\n\n')
        '''


if __name__ == '__main__':  # Measure start time
    main()

