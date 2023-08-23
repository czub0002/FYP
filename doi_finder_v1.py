from bs4 import BeautifulSoup
from dateutil import parser
import html
import re
import cProfile
import time


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
        # self.pubdate = self.get_pubdate()
        self.journal = self.get_journal()
        self.url = self.get_article_link()

        # Information from article webpage
        detailed_article = DetailedArticleInfo(self.doi)
        self.type = detailed_article.type
        self.references = detailed_article.references
        self.dates = detailed_article.dates

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
        title = string_cleaner(self.html_content[start_of_title:end_of_title])

        return title

    def get_authors(self):
        """
        Retrieves a list of the authors for each paper
        :return: List of authors
        """
        author_list = []
        last_author = False
        doi_index = self.doi_index

        while not last_author:
            author_query = "/author/"
            author_index = self.html_content.find(author_query, doi_index)

            # searches for start and end indexes of the author name
            start_of_name = self.html_content.find(">", author_index) + 1
            end_name_index = self.html_content.find("</a>", start_of_name)

            # cleans string if it contains html tags
            author = string_cleaner(self.html_content[start_of_name:end_name_index])
            author_list.append(author)

            doi_index = end_name_index

            # check if final author name
            last_author_query = '</a></span></span>'
            if self.html_content[end_name_index:end_name_index + len(last_author_query)] == last_author_query:
                last_author = True

        return author_list

    def get_journal(self):
        """
        Gets the journal name
        :return: string containing journal name
        """
        # searches for start and end indexes of the title
        start_of_title = self.html_content.find("<title>") + len("<title>")
        end_of_title = self.html_content.find("</title>")

        # cleans string if it contains html tags
        journal_title = string_cleaner(self.html_content[start_of_title:end_of_title])

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
    def __init__(self, doi):
        self.doi = doi
        self.article = self.get_article()
        self.type = self.get_article_type()
        self.references = self.get_references()
        self.dates = self.get_dates()

    def get_article(self):
        # -----------------------------------------------------------------
        # TODO - Remove when web scraping
        with open('web_link.html', 'r', encoding='utf-8') as html_file:
            file = html_file.read()

        soup = BeautifulSoup(file, 'html.parser')
        article = soup.get_text()

        return article
        # ------------------------------------------------------------------

    def get_article_type(self):
        query = "toc-heading"
        # searches for start and end indexes of the article link
        search_query = self.article.find(query)
        start_of_type = self.article.find(">", search_query) + 1
        end_of_type = self.article.find("</div>", start_of_type)

        article_type = self.article[start_of_type:end_of_type]

        return article_type

    def get_references(self):
        ref_list = []
        query = "class=\"references"
        # searches for start and end indexes of the article link
        search_query = self.article.find(query)
        last_ref = False
        last_ref_id = self.article.find('</li></ul></div>', search_query)

        while not last_ref:
            start_of_ref = self.article.find("<li", search_query)
            end_of_ref = self.article.find("</li>", start_of_ref)

            if start_of_ref < last_ref_id:
                ref = string_cleaner(self.article[start_of_ref:end_of_ref])
                ref_list.append(ref)
                search_query = end_of_ref
            else:
                last_ref = True

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
    # Read the HTML file
    with open('webpage.html', 'r', encoding='utf-8') as html_file:
        source_content = html_file.read()

    # Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(source_content, 'html.parser')

    # Extract text content from the parsed HTML
    html_file = soup.get_text()

    info = DataScraper(html_file)

    print("No. of unique DOIs: " + str(len(info.data)))

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


if __name__ == '__main__':
    start_time = time.time()  # Measure start time

    cProfile.run("main()")

    end_time = time.time()  # Measure end time
    elapsed_time = end_time - start_time
    print(f"Script execution time: {elapsed_time:.2f} seconds")

