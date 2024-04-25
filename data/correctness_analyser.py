import re
from dateutil.parser import ParserError
import string
from thefuzz import fuzz
import author_fuzzy_compare
from pandas import *
import pandas as pd
from dateutil import parser
import ast

# Convert data to dictionaries
elsevier_xls = ExcelFile('elsevier_data.xlsx')
elsevier_df = elsevier_xls.parse(elsevier_xls.sheet_names[0])
wos_elsevier_xls = ExcelFile('elsevier_wos_data.xlsx')
wos_elsevier_df = wos_elsevier_xls.parse(wos_elsevier_xls.sheet_names[0])

wiley_xls = ExcelFile('wiley_data.xlsx')
wiley_df = wiley_xls.parse(wiley_xls.sheet_names[0])
wos_wiley_xls = ExcelFile('wiley_wos_data.xlsx')
wos_wiley_df = wos_wiley_xls.parse(wos_wiley_xls.sheet_names[0])

tandf_xls = ExcelFile('tandf_data.xlsx')
tandf_df = tandf_xls.parse(tandf_xls.sheet_names[0])
wos_tandf_xls = ExcelFile('tandf_wos_data.xlsx')
wos_tandf_df = wos_tandf_xls.parse(wos_tandf_xls.sheet_names[0])

springer_xls = ExcelFile('springer_data.xlsx')
springer_df = springer_xls.parse(springer_xls.sheet_names[0])
wos_springer_xls = ExcelFile('springer_wos_data.xlsx')
wos_springer_df = wos_springer_xls.parse(wos_springer_xls.sheet_names[0])

# DONE
"""
- Article title
- Type
- Journal
    - pub year
    - pub date
    - edition
        - uid/volume
        - issue
        - part
    - name
- Authors
"""


class Correctness:
    def __init__(self, pub_data, wos_data):
        self.pub_data = pub_data
        self.wos_data = wos_data

    def pub_year(self):
        counter = {
            "correct_counter": 0,
            "missing_counter": 0,
            "incorrect_counter": 0,
            "total": 0
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_paper_pub_year = pub_paper["publication_year"]
            wos_paper_pub_year = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Publication Year"].values[0]

            if pd.isna(pub_paper_pub_year):
                continue
            else:
                if pd.isna(wos_paper_pub_year):
                    counter["missing_counter"] += 1
                elif pub_paper_pub_year != wos_paper_pub_year:
                    counter["incorrect_counter"] += 1
                elif pub_paper_pub_year == wos_paper_pub_year:
                    counter["correct_counter"] += 1

                counter["total"] += 1

        if counter['total']:
            print("PUBLISH YEAR")
            print(counter)
            print(f"Correct: {((counter['correct_counter'] / counter['total']) * 100):.2f}%")
            print(f"Incorrect: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")
            print(f"Missing: {((counter['missing_counter'] / counter['total']) * 100):.2f}%")

    def publication_date(self):
        counter = {
            "correct_date_counter": 0,
            "incorrect_date_counter": 0,
            "correct_month_counter": 0,
            "partial_month_counter": 0,
            "missing_counter": 0,
            "incorrect_counter": 0,
            "total": 0
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]

            # TODO - note this distinction
            # pub_paper_pub_date = pub_paper["received_date"]
            # pub_paper_pub_date = pub_paper["accepted_date"]
            pub_paper_pub_date = pub_paper["published_date"]

            wos_paper_pub_date = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Publication Date"].values[0]

            if pd.isna(pub_paper_pub_date):
                continue
            else:
                counter["total"] += 1

                if pd.isna(wos_paper_pub_date):
                    counter["missing_counter"] += 1
                else:
                    try:
                        parsed_date_month = parser.parse(wos_paper_pub_date, fuzzy=True).month

                        if parsed_date_month == pub_paper_pub_date.month:
                            counter["correct_month_counter"] += 1

                            # Define a regular expression pattern to match month and number
                            pattern = r'(?:(\d{4})\s+)?([A-Za-z]+)\s*(\d+)?'

                            # Use re.findall to search for all occurrences of the pattern in the input string
                            matches = re.findall(pattern, wos_paper_pub_date)

                            # Iterate over the matches and extract the year, month, and number
                            for match in matches:
                                date = match[2] if match[2] else None

                                if date:
                                    if int(date) == pub_paper_pub_date.day:
                                        counter["correct_date_counter"] += 1
                                    else:
                                        counter["incorrect_date_counter"] += 1
                        else:
                            counter["incorrect_counter"] += 1
                    except ParserError:
                        counter["incorrect_counter"] += 1
                    except ValueError:
                        if '-' in wos_paper_pub_date:
                            wos_paper_pub_month = wos_paper_pub_date.split('-')
                            if pub_paper_pub_date.month in \
                                    range(parser.parse(wos_paper_pub_month[0], fuzzy=True).month,
                                          parser.parse(wos_paper_pub_month[1], fuzzy=True).month+1):
                                counter["partial_month_counter"] += 1
                            else:
                                counter["incorrect_counter"] += 1
                        else:
                            counter["incorrect_counter"] += 1
                    except TypeError:
                        # Dont count large integer values - due to date time conversion in excel
                        counter["total"] -= 1

        if counter['total']:
            print("PUBLISH DATES")
            print(counter)
            print(f"correct_date_counter: {((counter['correct_date_counter'] / counter['total']) * 100):.2f}%")
            print(f"incorrect_date_counter: {((counter['incorrect_date_counter'] / counter['total']) * 100):.2f}%")
            print(f"correct_month_counter: {((counter['correct_month_counter'] / counter['total']) * 100):.2f}%")
            print(f"partial_month_counter: {((counter['partial_month_counter'] / counter['total']) * 100):.2f}%")
            print(f"missing_counter: {((counter['missing_counter'] / counter['total']) * 100):.2f}%")
            print(f"incorrect_counter: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")

    def journal_name(self):
        counter = {
            "correct_counter": 0,
            "likely_correct": 0,
            "missing_counter": 0,
            "incorrect_counter": 0,
            "total": 0
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_journal_name = pub_paper["journal"].lower()
            pub_paper_title = pub_paper["title"].lower()
            wos_journal_name = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Source Title"].values[0].lower()

            if pd.isna(pub_journal_name) or pub_journal_name == pub_paper_title:
                continue
            else:
                counter["total"] += 1

                if pd.isna(wos_journal_name):
                    counter["missing_counter"] += 1

                elif fuzz.ratio(pub_journal_name, wos_journal_name) == 100 or \
                        fuzz.partial_ratio(pub_journal_name, wos_journal_name) == 100:
                    counter["correct_counter"] += 1

                elif (fuzz.partial_ratio(pub_journal_name, wos_journal_name) > 95) or \
                        (fuzz.ratio(pub_journal_name, wos_journal_name) > 80):
                    counter["likely_correct"] += 1
                else:
                    counter["incorrect_counter"] += 1

        if counter['total']:
            print("JOURNAL NAME")
            print(counter)
            print(f"correct_counter: {((counter['correct_counter'] / counter['total']) * 100):.2f}%")
            print(f"likely_correct: {((counter['likely_correct'] / counter['total']) * 100):.2f}%")
            print(f"missing_counter: {((counter['missing_counter'] / counter['total']) * 100):.2f}%")
            print(f"incorrect_counter: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")

    def journal_edition(self):
        counter = {
            "all_correct_counter": 0,
            "correct_volume": 0,
            "correct_issue": 0,
            "correct_part": 0,
            "missing_volume": 0,
            "missing_issue": 0,
            "missing_part": 0,
            "incorrect_volume": 0,
            "incorrect_issue": 0,
            "incorrect_part": 0,
            "incorrect_counter": 0,
            "total_volume": 0,
            "total_issue": 0,
            "total_part": 0,
            "total": 0
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_journal_ed = \
                [pub_paper["uid"], pub_paper["issue"], pub_paper["part"]]
            wos_journal_ed = \
                [self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Volume"].values[0],
                 self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Issue"].values[0],
                 self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Part Number"].values[0]]

            # Checks if all vales of pub data are missing
            nan_count = 0
            for i in range(len(pub_journal_ed)):
                if str(pub_journal_ed[i]) == 'nan':
                    nan_count += 1

            if nan_count == 3:
                continue
            else:
                counter["total"] += 1

            all_correct = 0
            incorrect = 0
            for i in range(len(pub_journal_ed)):
                key = ['volume', 'issue', 'part']
                if str(pub_journal_ed[i]) == 'nan':
                    continue
                else:
                    counter["total_" + key[i]] += 1
                    if pd.isna(wos_journal_ed[i]):
                        counter["missing_" + key[i]] += 1
                    elif str(pub_journal_ed[i]) == str(wos_journal_ed[i]):
                        counter["correct_" + key[i]] += 1
                        all_correct += 1
                    elif '-' in str(wos_journal_ed[i]):
                        wos_journal_ed_range = wos_journal_ed[i].split('-')
                        if pub_journal_ed[i] in range(int(wos_journal_ed_range[0]), int(wos_journal_ed_range[-1])+1):
                            counter["correct_" + key[i]] += 1
                    # Parsing error, don't count
                    elif str(wos_journal_ed[i]).isnumeric():
                        if int(wos_journal_ed[i]) > 1000:
                            counter["total"] -= 1
                            counter["total_" + key[i]] -= 1
                        else:
                            counter["incorrect_" + key[i]] += 1
                    else:
                        counter["incorrect_" + key[i]] += 1
                        incorrect += 1

            # Checks if all the data from pub is in wos
            if all_correct == (len(pub_journal_ed) - nan_count):
                counter["all_correct_counter"] += 1

            # If one is incorrect, the paper is labelled incorrect - not by individual units
            if incorrect > 0:
                counter["incorrect_counter"] += 1

        if counter['total']:
            print("JOURNAL EDITION")
            print(counter)
            print(f"all_correct_counter: {((counter['all_correct_counter'] / counter['total']) * 100):.2f}%")
        if counter['total_volume']:
            print(f"correct_volume: {((counter['correct_volume'] / counter['total_volume']) * 100):.2f}%")
        if counter['total_issue']:
            print(f"correct_issue: {((counter['correct_issue'] / counter['total_issue']) * 100):.2f}%")
        if counter['total_part']:
            print(f"correct_part: {((counter['correct_part'] / counter['total_part']) * 100):.2f}%")
        if counter['total_volume']:
            print(f"missing_volume: {((counter['missing_volume'] / counter['total_volume']) * 100):.2f}%")
        if counter['total_issue']:
            print(f"missing_issue: {((counter['missing_issue'] / counter['total_issue']) * 100):.2f}%")
        if counter['total_part']:
            print(f"missing_part: {((counter['missing_part'] / counter['total_part']) * 100):.2f}%")
        if counter['total_volume']:
            print(f"incorrect_volume: {((counter['incorrect_volume'] / counter['total_volume']) * 100):.2f}%")
        if counter['total_issue']:
            print(f"incorrect_issue: {((counter['incorrect_issue'] / counter['total_issue']) * 100):.2f}%")
        if counter['total_part']:
            print(f"incorrect_part: {((counter['incorrect_part'] / counter['total_part']) * 100):.2f}%")
        if counter['total']:
            print(f"incorrect_counter: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")

    def paper_type(self):
        counter = {
            "correct_counter": 0,
            "missing_counter": 0,
            "incorrect_counter": 0,
            "total": 0
        }

        incorrect_outcomes = {}

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_paper_type = str(pub_paper["type"]).lower()
            wos_paper_type = \
                str(self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Document Type"].values[0]).lower()

            if pub_paper_type == 'nan':
                continue
            else:
                if pd.isna(wos_paper_type):
                    counter["missing_counter"] += 1
                elif fuzz.ratio(pub_paper_type, wos_paper_type) == 100:
                    counter["correct_counter"] += 1
                elif fuzz.partial_ratio(pub_paper_type, wos_paper_type) == 100:
                    counter["correct_counter"] += 1
                else:
                    counter["incorrect_counter"] += 1
                    key1 = pub_paper_type
                    key2 = wos_paper_type
                    incorrect_outcomes.setdefault(key1, {})
                    incorrect_outcomes[key1].setdefault(key2, 0)

                    incorrect_outcomes[key1][key2] += 1

                counter["total"] += 1

        print('INCORRECT TYPES')
        # Flatten the dictionary into a list of tuples (count, WoS Type, Pub Type)
        data = [(count, wos_type, pub_type) for pub_type, wos_types in incorrect_outcomes.items() for wos_type, count in
                wos_types.items()]
        # Sort the data by the counter in descending order
        data_sorted = sorted(data, key=lambda x: x[0], reverse=True)
        # Display the resulting sorted data in a tabular format
        headers = ["Counter", "WoS Type", "Publisher Type"]
        # print(tabulate(data_sorted, headers=headers))
        # print()

        if counter['total']:
            print("ARTICLE TYPE")
            print(counter)
            print(f"Correct: {((counter['correct_counter'] / counter['total']) * 100):.2f}%")
            print(f"Incorrect: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")
            print(f"Missing: {((counter['missing_counter'] / counter['total']) * 100):.2f}%")

    def authors(self):
        counter = {
            "correct_counter": 0,
            "missing_authors_counter": 0,
            "missing_data_counter": 0,
            "incorrect_counter": 0,
            "total_papers": 0,
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_paper_authors = pub_paper["authors"]
            wos_paper_authors = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Author Full Names"].values[0]
            wos_paper_group_authors = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Group Authors"].values[0]

            skip_outer_loop = False

            if pd.isna(pub_paper_authors):
                continue
            else:
                counter["total_papers"] += 1

                if pd.isna(wos_paper_authors):
                    # WoS missing authors
                    counter["missing_data_counter"] += 1
                    continue

                pub_paper_authors = ast.literal_eval(pub_paper_authors)
                wos_paper_authors = wos_paper_authors.split(';')
                if str(wos_paper_group_authors) != 'nan':
                    wos_paper_group_authors = str(wos_paper_group_authors).split(';')
                    wos_paper_authors = wos_paper_authors + wos_paper_group_authors

                # Don't include to stats where publisher has not listed author but wos has
                if len(pub_paper_authors) == 0:
                    counter["total_papers"] -= 1
                    continue

                if len(pub_paper_authors) == len(wos_paper_authors):
                    pub_incorrect, wos_incorrect = \
                        author_fuzzy_compare.check_same_person(pub_paper_authors, wos_paper_authors)
                    if len(pub_incorrect) == 0 and len(wos_incorrect) == 0:
                        # all authors listed and are matched
                        counter["correct_counter"] += 1
                    else:
                        # Check if name contains mostly special characters
                        for name in pub_incorrect:
                            if self.special_char_check(name):
                                counter["total_papers"] -= 1
                                skip_outer_loop = True
                                break

                        if skip_outer_loop:
                            continue

                        # Same number of authors listed, different authors listed
                        counter["incorrect_counter"] += 1
                        # print("INCORRECT AUTHORS - doi: " + pub_paper_doi)
                        # print(pub_incorrect)
                        # print(wos_incorrect)
                        # print()
                else:
                    # # Different number of authors listed
                    # print("MISSING AUTHORS - doi: " + pub_paper_doi)
                    # print("No. Authors: " + str(len(pub_paper_authors)) + "     " + str(pub_paper_authors))
                    # print("No. Authors: " + str(len(wos_paper_authors)) + "     " + str(wos_paper_authors))
                    # print()
                    counter["missing_authors_counter"] += 1

        if counter['total_papers']:
            print("AUTHORS CORRECTNESS")
            print(counter)
            print(f"Correct: {((counter['correct_counter'] / counter['total_papers']) * 100):.2f}%")
            print(f"Missing Authors: {((counter['missing_authors_counter'] / counter['total_papers']) * 100):.2f}%")
            print(f"Incorrect: {((counter['incorrect_counter'] / counter['total_papers']) * 100):.2f}%")
            print(f"Missing Data: {((counter['missing_data_counter'] / counter['total_papers']) * 100):.2f}%")

    def article_title(self):
        counter = {
            "exact_correct_counter": 0,
            "mostly_correct_counter": 0,
            "missing_counter": 0,
            "incorrect_counter": 0,
            "total": 0
        }

        for index, pub_paper in self.pub_data.iterrows():
            pub_paper_doi = pub_paper["wos_doi"]
            pub_paper_title = pub_paper["title"].lower()
            wos_paper_title = self.wos_data[self.wos_data['DOI'] == pub_paper_doi]["Article Title"].values[0].lower()

            if pd.isna(pub_paper_title):
                continue
            else:
                counter["total"] += 1

                if pd.isna(wos_paper_title):
                    # WoS missing authors
                    counter["missing_data_counter"] += 1
                    continue

                if self.special_char_check(pub_paper_title):
                    counter["total"] -= 1
                    continue

                if str(pub_paper["type"]).lower() == pub_paper_title:
                    counter["total"] -= 1
                    continue

                # Titles are identical
                if pub_paper_title == wos_paper_title:
                    counter['exact_correct_counter'] += 1

                # Titles are mostly the same
                elif (fuzz.partial_ratio(pub_paper_title, wos_paper_title) > 95) or \
                        (fuzz.ratio(pub_paper_title, wos_paper_title) > 80):
                    counter['mostly_correct_counter'] += 1

                else:
                    # print("INCORRECT TITLE: doi - " + pub_paper_doi)
                    # print("Perfect Ratio: " + str(fuzz.ratio(pub_paper_title, wos_paper_title)))
                    # print("Partial Ratio: " + str(fuzz.partial_ratio(pub_paper_title, wos_paper_title)))
                    # print("Publisher: " + pub_paper_title)
                    # print("WoS: " + wos_paper_title)
                    # print()
                    counter['incorrect_counter'] += 1

        if counter['total']:
            print("TITLE CORRECTNESS")
            print(counter)
            print(f"Exact Correct: {((counter['exact_correct_counter'] / counter['total']) * 100):.2f}%")
            print(f"Mostly Correct: {((counter['mostly_correct_counter'] / counter['total']) * 100):.2f}%")
            print(f"Missing Authors: {((counter['missing_counter'] / counter['total']) * 100):.2f}%")
            print(f"Incorrect: {((counter['incorrect_counter'] / counter['total']) * 100):.2f}%")

    def special_char_check(self, input_string):
        spec_char_string = False

        alphabet_chars = set(string.ascii_letters)
        num_special_chars = sum(1 for char in input_string if char not in alphabet_chars)
        num_alphabet_chars = sum(1 for char in input_string if char in alphabet_chars)

        # If there are more special characters than non-special characters, return True
        # Otherwise, return False
        if num_special_chars > num_alphabet_chars:
            spec_char_string = True

        return spec_char_string


pub_df, wos_df = springer_df, wos_springer_df

# Correctness(pub_df, wos_df).pub_year()
# print()
# Correctness(pub_df, wos_df).publication_date()
# print()
# Correctness(pub_df, wos_df).journal_name()
# print()
# Correctness(pub_df, wos_df).journal_edition()
# print()
# Correctness(pub_df, wos_df).paper_type()
# print()
Correctness(pub_df, wos_df).authors()
print()
# Correctness(pub_df, wos_df).article_title()
# print()