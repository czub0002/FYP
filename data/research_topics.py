from tabulate import tabulate
from pandas import *
import pycountry


class ResearchTopics:
    def __init__(self, wos_data):
        self.wos_data = wos_data
        self.total_papers = 0

        self.citations_per_year_dict = {}
        self.authors_vs_citations_dict = {}
        self.keywords_vs_citations_dict = {}
        self.journals_vs_citations_dict = {}
        self.journals_vs_references_dict = {}
        self.doctype_vs_citations_dict = {}
        self.doctype_vs_references_dict = {}
        self.publisher_vs_citations_dict = {}
        self.publisher_vs_references_dict = {}
        self.city_vs_citations_dict = {}
        self.publisher_city_dict = {}
        self.funding_orgs_vs_citations_dict = {"Funded": [], "Unfunded": []}
        self.citations_vs_research_areas_dict = {}
        self.country_vs_citation_dict = {}
        self.unique_country_vs_citation_dict = {}
        self.length_vs_citation_dict = {}
        self.references_vs_citation_dict = {}
        self.affiliations_vs_year_dict = {}

        self.country_dict = {}
        for country in pycountry.countries:
            self.country_dict[country.name] = {
                'official_name': country.official_name,
                'common_name': country.common_name,
                'alpha_2': country.alpha_2,
                'alpha_3': country.alpha_3
            }

        custom_countries = {
            'England': {'official_name': 'England', 'common_name': 'England', 'alpha_2': 'GB', 'alpha_3': 'ENG'},
            'Scotland': {'official_name': 'Scotland', 'common_name': 'Scotland', 'alpha_2': 'GB', 'alpha_3': 'SCT'},
            'Wales': {'official_name': 'Wales', 'common_name': 'Wales', 'alpha_2': 'GB', 'alpha_3': 'WLS'},
            'Northern Ireland': {'official_name': 'Northern Ireland', 'common_name': 'Northern Ireland', 'alpha_2': 'GB', 'alpha_3': 'NIR'},
            'Russia': {'official_name': 'Russia', 'common_name': 'Russia', 'alpha_2': 'RU', 'alpha_3': 'RUS'},
            'Turkey': {'official_name': 'Turkey', 'common_name': 'Turkey', 'alpha_2': 'TR', 'alpha_3': 'TUR'},
            'Yugoslavia': {'official_name': 'Jugoslavia', 'common_name': 'Yugoslavia', 'alpha_2': 'YU', 'alpha_3': 'YUG'},
            'United Arab Emirates': {'official_name': 'United Arab Emirates', 'common_name': 'U Arab Emirates', 'alpha_2': 'UA', 'alpha_3': 'UAE'}
        }

        # Update the dictionary with custom countries
        self.country_dict.update(custom_countries)

        for index, wos_paper in self.wos_data.iterrows():
            self.total_papers += 1
            self.citations_per_year(wos_paper)
            self.authors_vs_citations(wos_paper)
            self.keywords_vs_citations(wos_paper)
            self.journals_vs_citations(wos_paper)
            self.doctype_vs_citations(wos_paper)
            self.publisher_vs_citations(wos_paper)
            self.publisher_vs_references(wos_paper)
            self.city_vs_citations(wos_paper)
            self.funding_orgs_vs_citations(wos_paper)
            self.citations_vs_research_areas(wos_paper)
            self.country_vs_citation(wos_paper)
            self.length_vs_citation(wos_paper)
            self.references_vs_citation(wos_paper)
            self.affiliations_vs_year(wos_paper)

        self.citations_vs_pubyear_averages = self.dict_average_calc(self.citations_per_year_dict)
        self.authors_vs_citations_averages = self.dict_average_calc(self.authors_vs_citations_dict)
        self.keywords_vs_citations_averages = self.dict_average_calc(self.keywords_vs_citations_dict)
        self.journals_vs_citations_averages = self.dict_average_calc(self.journals_vs_citations_dict)
        self.journals_vs_references_averages = self.dict_average_calc(self.journals_vs_references_dict)
        self.doctype_vs_citations_averages = self.dict_average_calc(self.doctype_vs_citations_dict)
        self.doctype_vs_references_averages = self.dict_average_calc(self.doctype_vs_references_dict)
        self.publisher_vs_citations_averages = self.dict_average_calc(self.publisher_vs_citations_dict)
        self.publisher_vs_references_averages = self.dict_average_calc(self.publisher_vs_references_dict)
        self.city_vs_citations_averages = self.dict_average_calc(self.city_vs_citations_dict)
        self.funding_orgs_vs_citations_averages = self.dict_average_calc(self.funding_orgs_vs_citations_dict)
        self.citations_vs_research_areas_averages = {}
        self.country_vs_citation_averages = self.dict_average_calc(self.country_vs_citation_dict)
        self.unique_country_vs_citation_averages = self.dict_average_calc(self.unique_country_vs_citation_dict)
        self.length_vs_citation_averages = self.dict_average_calc(self.length_vs_citation_dict)
        self.references_vs_citation_averages = self.dict_average_calc(self.references_vs_citation_dict)

        # Iterate over each research area in the citations_vs_research_areas_dict
        for area, data in self.citations_vs_research_areas_dict.items():
            # Calculate the averages
            avg_citations = sum(data["citations"]) / len(data["citations"])
            avg_usage_180 = sum(data["usage_180"]) / len(data["usage_180"])
            avg_usage_2013 = sum(data["usage_2013"]) / len(data["usage_2013"])

            # Store the averages in the averages_dict
            self.citations_vs_research_areas_averages[area] = {
                "avg_citations": avg_citations,
                "avg_usage_180": avg_usage_180,
                "avg_usage_2013": avg_usage_2013
            }

        # self.print_results()

    def citations_per_year(self, wos_paper):
        pub_year = str(wos_paper['Publication Year'])

        if str(pub_year) == 'nan':
            return
        else:
            pub_year = int(wos_paper['Publication Year'])
            key = pub_year
            
            citations = wos_paper['Times Cited, All Databases']
            self.citations_per_year_dict.setdefault(key, [])
            
            self.citations_per_year_dict[key].append(citations)

    def authors_vs_citations(self, wos_paper):
        authors = wos_paper['Authors']

        if str(authors) == 'nan':
            return
        else:
            authors = authors.split(";")
            if authors[-1] == "":
                authors.pop()
            authors_len = len(authors)

            key = authors_len
            citations = wos_paper['Times Cited, All Databases']

            self.authors_vs_citations_dict.setdefault(key, [])
            self.authors_vs_citations_dict[key].append(citations)

    def keywords_vs_citations(self, wos_paper):
        keywords = wos_paper['Keywords Plus']

        if str(keywords) == 'nan':
            return
        else:
            keywords = keywords.split(";")
            if keywords[-1] == "":
                keywords.pop()
            keywords_len = len(keywords)

            key = keywords_len
            citations = wos_paper['Times Cited, All Databases']

            self.keywords_vs_citations_dict.setdefault(key, [])
            self.keywords_vs_citations_dict[key].append(citations)

    def journals_vs_citations(self, wos_paper):
        journal = wos_paper['Source Title']

        if str(journal) == 'nan':
            return
        else:
            citations = wos_paper['Times Cited, All Databases']
            references = wos_paper['Cited Reference Count']
            key = journal

            self.journals_vs_citations_dict.setdefault(key, [])
            self.journals_vs_citations_dict[key].append(citations)

            self.journals_vs_references_dict.setdefault(key, [])
            self.journals_vs_references_dict[key].append(references)

    def doctype_vs_citations(self, wos_paper):
        doctype = wos_paper['Document Type']

        if str(doctype) == 'nan':
            return
        else:
            citations = wos_paper['Times Cited, All Databases']
            references = wos_paper['Cited Reference Count']
            key = doctype

            self.doctype_vs_citations_dict.setdefault(key, [])
            self.doctype_vs_citations_dict[key].append(citations)

            self.doctype_vs_references_dict.setdefault(key, [])
            self.doctype_vs_references_dict[key].append(references)

    def publisher_vs_citations(self, wos_paper):
        publisher = wos_paper['Publisher']

        if str(publisher) == 'nan':
            return
        else:
            citations = wos_paper['Times Cited, All Databases']
            key = publisher

            self.publisher_vs_citations_dict.setdefault(key, [])
            self.publisher_vs_citations_dict[key].append(citations)

    def publisher_vs_references(self, wos_paper):
        publisher = wos_paper['Publisher']

        if str(publisher) == 'nan':
            return
        else:
            references = wos_paper['Cited Reference Count']
            key = publisher

            self.publisher_vs_references_dict.setdefault(key, [])
            self.publisher_vs_references_dict[key].append(references)

    def city_vs_citations(self, wos_paper):
        city = wos_paper['Publisher City']
        publisher = wos_paper['Publisher']

        if str(city) == 'nan':
            return
        else:
            citations = wos_paper['Times Cited, All Databases']
            key = city

            self.city_vs_citations_dict.setdefault(key, [])
            self.publisher_city_dict.setdefault(key, [])

            self.city_vs_citations_dict[key].append(citations)

            if publisher not in self.publisher_city_dict[key]:
                self.publisher_city_dict[key].append(publisher)

    def funding_orgs_vs_citations(self, wos_paper):
        funding_org = wos_paper['Funding Orgs']
        citations = wos_paper['Times Cited, All Databases']

        if str(funding_org) == 'nan':
            self.funding_orgs_vs_citations_dict["Unfunded"].append(citations)
            return
        else:
            self.funding_orgs_vs_citations_dict["Funded"].append(citations)

    def citations_vs_research_areas(self, wos_paper):
        research_area = wos_paper['Research Areas']
        research_area_list = research_area.split(";")
        citations = wos_paper['Times Cited, All Databases']
        usage_180 = wos_paper['180 Day Usage Count']
        usage_2013 = wos_paper['Since 2013 Usage Count']

        if research_area_list[-1] == "":
            research_area_list.pop()

        if str(research_area) == 'nan':
            return
        else:
            for area in research_area_list:
                self.citations_vs_research_areas_dict.setdefault(area,
                                                                 {"citations": [], "usage_180": [], "usage_2013": []})
                self.citations_vs_research_areas_dict[area]["citations"].append(citations)
                self.citations_vs_research_areas_dict[area]["usage_180"].append(usage_180)
                self.citations_vs_research_areas_dict[area]["usage_2013"].append(usage_2013)

    def country_vs_citation(self, wos_paper):
        author_address = wos_paper['Addresses']
        unique_countries = []

        if str(author_address) == 'nan':
            return
        else:
            author_address = author_address.split(";")
            citations = wos_paper['Times Cited, All Databases']
            for address in author_address:
                if "Bosnia & Herceg" in address:
                    address = 'Bosnia and Herzegovina'
                for country in self.country_dict:
                    if country in address or \
                            self.country_dict[country]["official_name"] in address or \
                            self.country_dict[country]["common_name"] in address or \
                            self.country_dict[country]["alpha_2"] in address or \
                            self.country_dict[country]["alpha_3"] in address:
                        key = country

                        if key not in unique_countries:
                            unique_countries.append(key)

                        self.country_vs_citation_dict.setdefault(key, [])
                        self.country_vs_citation_dict[key].append(citations)

            unique_countries_counter = len(unique_countries)
            if unique_countries_counter == 0:
                print('Country Not Found')
            else:
                self.unique_country_vs_citation_dict.setdefault(unique_countries_counter, [])
                self.unique_country_vs_citation_dict[unique_countries_counter].append(citations)

    def length_vs_citation(self, wos_paper):
        number_of_pages = wos_paper['Number of Pages']
        citations = wos_paper['Times Cited, All Databases']

        if str(number_of_pages) == 'nan':
            return
        else:
            key = number_of_pages

            self.length_vs_citation_dict.setdefault(key, [])
            self.length_vs_citation_dict[key].append(citations)

    def references_vs_citation(self, wos_paper):
        references = wos_paper['Cited Reference Count']
        citations = wos_paper['Times Cited, All Databases']

        if str(references) == 'nan' or str(citations) == 'nan':
            return
        else:
            key = references

            self.references_vs_citation_dict.setdefault(key, [])
            self.references_vs_citation_dict[key].append(citations)

    def affiliations_vs_year(self, wos_paper):
        affiliations = wos_paper['Affiliations']
        pub_paper_year = wos_paper["Publication Year"]

        key = str(pub_paper_year)

        if str(affiliations) == 'nan':
            self.affiliations_vs_year_dict.setdefault(key, {'True': 0, 'False': 0})
            self.affiliations_vs_year_dict[key]["False"] = self.affiliations_vs_year_dict[key]["False"] + 1
        else:
            self.affiliations_vs_year_dict.setdefault(key, {'True': 0, 'False': 0})
            self.affiliations_vs_year_dict[key]["True"] = self.affiliations_vs_year_dict[key]["True"] + 1


    def dict_average_calc(self, results_dict):
        mean_dict = results_dict

        # Calculate the average for each list
        averages = {key: sum(values) / len(values) for key, values in mean_dict.items()}

        return averages

    def print_results(self):
        # NO. ARTICLES and AVE CITATIONS vs YEAR
        print('AVERAGE CITATIONS PER YEAR')
        # Sort the averages by list number
        sorted_averages = sorted(self.citations_vs_pubyear_averages.items(), key=lambda x: x[0])
        # Tabulate the sorted averages
        table = [["Publish Year", "Ave. Citations", "No. of Papers"]]
        for year, average in sorted_averages:
            list_length = len(self.citations_per_year_dict[year])
            table.append([year, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # NO. AUTHORS vs AVERAGE CITATIONS
        print('AVERAGE CITATIONS PER NO. OF AUTHORS')
        # Sort the averages by list number
        sorted_averages = sorted(self.authors_vs_citations_averages.items(), key=lambda x: x[0])
        # Tabulate the sorted averages
        table = [["No. of Authors", "Ave. Citations", "No. of Papers"]]
        for no_authors, average in sorted_averages:
            list_length = len(self.authors_vs_citations_dict[no_authors])
            table.append([no_authors, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # NO. KEYWORDS vs AVERAGE CITATIONS
        print('AVERAGE CITATIONS PER NO. OF KEYWORDS')
        # Sort the averages by list number
        sorted_averages = sorted(self.keywords_vs_citations_averages.items(), key=lambda x: x[0])
        # Tabulate the sorted averages
        table = [["No. of Keywords", "Ave. Citations", "No. of Papers"]]
        for keywords_no, average in sorted_averages:
            list_length = len(self.keywords_vs_citations_dict[keywords_no])
            table.append([keywords_no, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # JOURNALS vs AVERAGE CITATIONS
        print('AVERAGE CITATIONS PER JOURNAL')
        # Sort the averages by list number
        sorted_averages = sorted(self.journals_vs_citations_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Journal", "Ave. Citations", "No. of Papers"]]
        for journal, average in sorted_averages:
            list_length = len(self.journals_vs_citations_dict[journal])
            table.append([journal, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # JOURNALS vs AVERAGE REFERENCES
        print('AVERAGE REFERENCES PER JOURNAL')
        # Sort the averages by list number
        sorted_averages = sorted(self.journals_vs_references_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Journal", "Ave. References", "No. of Papers"]]
        for journal, average in sorted_averages:
            list_length = len(self.journals_vs_references_dict[journal])
            table.append([journal, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # DOCTYPE vs AVERAGE CITATIONS
        print('AVERAGE CITATIONS PER DOCUMENT TYPE')
        # Sort the averages by list number
        sorted_averages = sorted(self.doctype_vs_citations_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Document Type", "Ave. Citations", "No. of Papers"]]
        for doctype, average in sorted_averages:
            list_length = len(self.doctype_vs_citations_dict[doctype])
            table.append([doctype, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # DOCTYPE vs AVERAGE REFERENCES
        print('AVERAGE REFERENCES PER DOCUMENT TYPE')
        # Sort the averages by list number
        sorted_averages = sorted(self.doctype_vs_references_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Document Type", "Ave. References", "No. of Papers"]]
        for doctype, average in sorted_averages:
            list_length = len(self.doctype_vs_references_dict[doctype])
            table.append([doctype, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # AVERAGE CITATIONS FOR PUBLISHER
        print('AVERAGE CITATIONS PER PUBLISHER')
        # Sort the averages by list number
        sorted_averages = sorted(self.publisher_vs_citations_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Publisher", "Ave. Citations", "No. of Papers"]]
        for publisher, average in sorted_averages:
            list_length = len(self.publisher_vs_citations_dict[publisher])
            table.append([publisher, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # AVERAGE REFERENCES FOR PUBLISHER
        print('AVERAGE CITATIONS PER PUBLISHER')
        # Sort the averages by list number
        sorted_averages = sorted(self.publisher_vs_references_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Publisher", "Ave. References", "No. of Papers"]]
        for publisher, average in sorted_averages:
            list_length = len(self.publisher_vs_references_dict[publisher])
            table.append([publisher, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # AVERAGE CITATIONS PER PUBLISHER CITY
        print('AVERAGE CITATIONS PER PUBLISHER CITY')
        # Sort the averages by list number
        sorted_averages = sorted(self.city_vs_citations_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Publisher City", "Ave. Citations", "Publishers"]]
        for city, citations in sorted_averages:
            publisher_list = self.publisher_city_dict[city]
            table.append([city, citations, publisher_list])
        print(tabulate(table, headers="firstrow"))
        print()

        # NO. ARTICLES and AVE CITATIONS vs FUNDED
        print('AVERAGE CITATIONS FOR FUNDED/UNFUNDED PAPERS')
        # Sort the averages by list number
        sorted_averages = sorted(self.funding_orgs_vs_citations_averages.items(), key=lambda x: x[1])
        # Tabulate the sorted averages
        table = [["Funding", "Ave. Citations", "No. of Papers"]]
        for funding, average in sorted_averages:
            list_length = len(self.funding_orgs_vs_citations_dict[funding])
            table.append([funding, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # Print AVERAGE CITATIONS, AVERAGE USAGE 180, AVERAGE USAGE 2013, and NUMBER OF PAPERS
        print('AVERAGE METRICS PER RESEARCH AREA')
        # Sort the averages by list number
        sorted_averages = sorted(self.citations_vs_research_areas_averages.items(),
                                 key=lambda x: x[1]["avg_citations"], reverse=True)
        # Tabulate the sorted averages
        table = [["Research Area", "Ave. Citations", "Ave. Usage 180", "Ave. Usage 2013", "No. of Papers"]]
        for research_area, averages in sorted_averages:
            num_papers = len(self.citations_vs_research_areas_dict[research_area]["citations"])
            table.append(
                [research_area, averages["avg_citations"], averages["avg_usage_180"], averages["avg_usage_2013"],
                 num_papers])
        print(tabulate(table, headers="firstrow"))
        print()

        # AUTHOR COUNTRIES vs AVE CITATIONS
        print('AVERAGE CITATIONS PER AUTHOR COUNTRIES')
        # Sort the averages by list number
        sorted_averages = sorted(self.country_vs_citation_averages.items(), key=lambda x: x[1], reverse=True)
        # Tabulate the sorted averages
        table = [["Country", "Ave. Citations", "No. of Papers"]]
        for country, average in sorted_averages:
            list_length = len(self.country_vs_citation_dict[country])
            table.append([country, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # UNIQUE AUTHOR COUNTRIES vs AVE CITATIONS
        print('AVERAGE CITATIONS PER NUMBER OF UNIQUE AUTHOR COUNTRIES')
        # Sort the averages by list number
        sorted_averages = sorted(self.unique_country_vs_citation_averages.items(), key=lambda x: x[0], reverse=True)
        # Tabulate the sorted averages
        table = [["Unique Countries", "Ave. Citations", "No. of Papers"]]
        for country_count, average in sorted_averages:
            list_length = len(self.unique_country_vs_citation_dict[country_count])
            table.append([country_count, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # PAPER LENGTH vs AVE CITATIONS
        print('AVERAGE CITATIONS PER LENGTH OF PAPER')
        # Sort the averages by list number
        sorted_averages = sorted(self.length_vs_citation_averages.items(), key=lambda x: x[0], reverse=True)
        # Tabulate the sorted averages
        table = [["Length (Pages)", "Ave. Citations", "No. of Papers"]]
        for length, average in sorted_averages:
            list_length = len(self.length_vs_citation_dict[length])
            table.append([length, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # REFERENCES vs AVE CITATIONS
        print('AVERAGE CITATIONS PER NUMBER OF REFERENCES')
        # Sort the averages by list number
        sorted_averages = sorted(self.references_vs_citation_averages.items(), key=lambda x: x[0], reverse=True)
        # Tabulate the sorted averages
        table = [["No. of References", "Ave. Citations", "No. of Papers"]]
        for references, average in sorted_averages:
            list_length = len(self.references_vs_citation_dict[references])
            table.append([references, average, list_length])
        print(tabulate(table, headers="firstrow"))
        print()

        # AFFILIATIONS vs YEAR
        print('PERCENTAGE OF AFFILIATIONS PER YEAR')
        # Sort the averages by list number
        table = [["Year", "Affiliation %", "Total Papers"]]

        # Iterate through the sorted dictionary items by year
        for year, citations in sorted(self.affiliations_vs_year_dict.items()):
            # Calculate the total number of True and False values
            total_references = citations.get('True', 0) + citations.get('False', 0)
            # Calculate the percentage of True values
            if total_references > 0:
                affiliation_percentage = (citations.get('True', 0) / total_references) * 100
            else:
                affiliation_percentage = 0
            # Append the year, affiliation percentage, and total references to the table
            table.append([year, f"{affiliation_percentage:.2f}%", total_references])
        # Tabulate and print the results
        print(tabulate(table, headers="firstrow"))
        print()

        # TOTAL PAPERS
        print(f'TOTAL PAPERS: {self.total_papers}')
        print()


# Convert data to dictionaries
# wos_elsevier_xls = ExcelFile('elsevier_wos_data.xlsx')
# wos_elsevier_df = wos_elsevier_xls.parse(wos_elsevier_xls.sheet_names[0])
#
# wos_tandf_xls = ExcelFile('tandf_wos_data.xlsx')
# wos_tandf_df = wos_tandf_xls.parse(wos_tandf_xls.sheet_names[0])
#
# wos_springer_xls = ExcelFile('springer_wos_data.xlsx')
# wos_springer_df = wos_springer_xls.parse(wos_springer_xls.sheet_names[0])
#
# wos_df = wos_elsevier_df
#
# rt = ResearchTopics(wos_df)
# rt.print_results()


