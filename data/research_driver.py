import json
import sys

from research_topics import ResearchTopics
from pandas import *
import pandas as pd
from copy import deepcopy
import time


# Create the data object to pass to the ResearchTopics class
data_obj = {
    "citations_per_year_dict": {},
    "authors_vs_citations_dict": {},
    "keywords_vs_citations_dict": {},
    "journals_vs_citations_dict": {},
    "journals_vs_references_dict": {},
    "doctype_vs_citations_dict": {},
    "doctype_vs_references_dict": {},
    "publisher_vs_citations_dict": {},
    "publisher_vs_references_dict": {},
    "city_vs_citations_dict": {},
    "publisher_city_dict": {},
    "funding_orgs_vs_citations_dict": {"Funded": [], "Unfunded": []},
    "citations_vs_research_areas_dict": {},
    "country_vs_citation_dict": {},
    "unique_country_vs_citation_dict": {},
    "length_vs_citation_dict": {},
    "references_vs_citation_dict": {},
    "affiliations_vs_year_dict": {},
    "total_papers": 0,

    "citations_vs_research_areas_averages": {},
    "citations_per_year_averages": {},
    "authors_vs_citations_averages": {},
    "keywords_vs_citations_averages": {},
    "journals_vs_citations_averages": {},
    "journals_vs_references_averages": {},
    "doctype_vs_citations_averages": {},
    "doctype_vs_references_averages": {},
    "publisher_vs_citations_averages": {},
    "publisher_vs_references_averages": {},
    "city_vs_citations_averages": {},
    "funding_orgs_vs_citations_averages": {},
    "country_vs_citation_averages": {},
    "unique_country_vs_citation_averages": {},
    "length_vs_citation_averages": {},
    "references_vs_citation_averages": {},

}

default_values = {
    "citations_per_year_dict": {},
    "authors_vs_citations_dict": {},
    "keywords_vs_citations_dict": {},
    "journals_vs_citations_dict": {},
    "journals_vs_references_dict": {},
    "doctype_vs_citations_dict": {},
    "doctype_vs_references_dict": {},
    "publisher_vs_citations_dict": {},
    "publisher_vs_references_dict": {},
    "city_vs_citations_dict": {},
    "publisher_city_dict": {},
    "funding_orgs_vs_citations_dict": {"Funded": [], "Unfunded": []},
    "citations_vs_research_areas_dict": {},
    "country_vs_citation_dict": {},
    "unique_country_vs_citation_dict": {},
    "length_vs_citation_dict": {},
    "references_vs_citation_dict": {}
}

# Assuming you have a list of Excel file paths
excel_files = ['Copy of Taylor_Francis_Data_0007.xlsx', 'Copy of Taylor_Francis_Data_0008.xlsx', 'Copy of Taylor_Francis_Data_0009.xlsx']

for file_path in excel_files:
    start_time = time.time()
    print(f"Reading {file_path}.")
    values_copy = deepcopy(default_values)

    # Read data from each Excel file
    wos_paper = read_excel(file_path)

    # Create an instance of ResearchTopics with the data and data_obj
    rt = ResearchTopics(wos_paper, data_obj)

    # Process the data and update the data_obj
    for index, row in wos_paper.iterrows():
        data_obj['total_papers'] += 1
        rt.citations_per_year(row)
        rt.authors_vs_citations(row)
        rt.keywords_vs_citations(row)
        rt.journals_vs_citations(row)
        rt.doctype_vs_citations(row)
        rt.publisher_vs_citations(row)
        rt.publisher_vs_references(row)
        rt.city_vs_citations(row)
        rt.funding_orgs_vs_citations(row)
        rt.citations_vs_research_areas(row)
        rt.country_vs_citation(row)
        rt.length_vs_citation(row)
        rt.references_vs_citation(row)
        rt.affiliations_vs_year(row)

    # Calculate averages
    # List of keys to iterate over
    keys = [
        "citations_per_year_",
        "authors_vs_citations_",
        "keywords_vs_citations_",
        "journals_vs_citations_",
        "journals_vs_references_",
        "doctype_vs_citations_",
        "doctype_vs_references_",
        "publisher_vs_citations_",
        "publisher_vs_references_",
        "city_vs_citations_",
        "funding_orgs_vs_citations_",
        "country_vs_citation_",
        "unique_country_vs_citation_",
        "length_vs_citation_",
        "references_vs_citation_"
    ]

    # Iterate over each key and call rt.dict_average_calc, updating the data_obj dictionary
    for key in keys:
        rt.dict_average_calc(key)

    # Iterate over each research area in the citations_vs_research_areas_dict
    for area, data in data_obj["citations_vs_research_areas_dict"].items():
        # Calculate the averages
        avg_citations = sum(data["citations"]) / len(data["citations"])
        avg_usage_180 = sum(data["usage_180"]) / len(data["usage_180"])
        avg_usage_2013 = sum(data["usage_2013"]) / len(data["usage_2013"])

        # Store the averages in the averages_dict
        if area in data_obj["citations_vs_research_areas_averages"]:
            no_papers = data_obj["citations_vs_research_areas_averages"][area]["no_papers"]
            new_papers = len(data["citations"])
            combined_papers = no_papers + new_papers

            data_obj["citations_vs_research_areas_averages"][area]["avg_citations"] = \
                ((no_papers * data_obj["citations_vs_research_areas_averages"][area]["avg_citations"]) +
                 (new_papers * avg_citations))/combined_papers

            data_obj["citations_vs_research_areas_averages"][area]["avg_usage_180"] = \
                ((no_papers * data_obj["citations_vs_research_areas_averages"][area]["avg_usage_180"]) +
                 (new_papers * avg_citations))/combined_papers

            data_obj["citations_vs_research_areas_averages"][area]["avg_usage_2013"] = \
                ((no_papers * data_obj["citations_vs_research_areas_averages"][area]["avg_usage_2013"]) +
                 (new_papers * avg_citations))/combined_papers

            data_obj["citations_vs_research_areas_averages"][area]["no_papers"] = combined_papers

        else:
            data_obj["citations_vs_research_areas_averages"][area] = {
                "avg_citations": avg_citations,
                "avg_usage_180": avg_usage_180,
                "avg_usage_2013": avg_usage_2013,
                "no_papers": len(data["citations"])
            }

    data_obj.update(values_copy)

    # Save the data_obj state to a file after processing each Excel file for error handling
    # Use your preferred method to save the data_obj (e.g., pickle, JSON, etc.)
    with open('data_obj.json', 'w') as file:
        file.write('\n')
        file.write(file_path)
        json.dump(data_obj, file)

    print(f"{file_path} read in {time.time() - start_time:.2f} seconds.")
    print(f"Total papers: {rt.data_obj['total_papers']}")
    print()

def print_results(self):
    # Open an Excel file using pandas.ExcelWriter
    with pd.ExcelWriter('results.xlsx') as writer:
        # Define each sheet name and the respective list of data
        results = [
            ("Citations Per Year",
             sorted(self.data_obj['citations_per_year_averages'].items(), key=lambda x: x[0]),
             [["Publish Year", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Authors",
             sorted(self.data_obj['authors_vs_citations_averages'].items(), key=lambda x: x[0]),
             [["No. of Authors", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Keywords",
             sorted(self.data_obj['keywords_vs_citations_averages'].items(), key=lambda x: x[0]),
             [["No. of Keywords", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Journal",
             sorted(self.data_obj['journals_vs_citations_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Journal", "Ave. Citations", "No. of Papers"]]),
            ("References Per Journal",
             sorted(self.data_obj['journals_vs_references_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Journal", "Ave. References", "No. of Papers"]]),
            ("Citations Per Doc Type",
             sorted(self.data_obj['doctype_vs_citations_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Document Type", "Ave. Citations", "No. of Papers"]]),
            ("References Per Doc Type",
             sorted(self.data_obj['doctype_vs_references_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Document Type", "Ave. References", "No. of Papers"]]),
            ("Citations Per Publisher",
             sorted(self.data_obj['publisher_vs_citations_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Publisher", "Ave. Citations", "No. of Papers"]]),
            ("References Per Publisher",
             sorted(self.data_obj['publisher_vs_references_averages'].items(), key=lambda x: x[1]['average'],
                    reverse=True), [["Publisher", "Ave. References", "No. of Papers"]]),
            ("Citations Per City",
             sorted(self.data_obj['city_vs_citations_averages'].items(), key=lambda x: x[1]['average'], reverse=True),
             [["Publisher City", "Ave. Citations", "Publishers"]]),
            ("Citations For Funded Papers",
             sorted(self.data_obj['funding_orgs_vs_citations_averages'].items(), key=lambda x: x[1]['average']),
             [["Funding", "Ave. Citations", "No. of Papers"]]),
            ("Metrics Per Research Area",
             sorted(self.data_obj['citations_vs_research_areas_averages'].items(), key=lambda x: x[1]["avg_citations"],
                    reverse=True),
             [["Research Area", "Ave. Citations", "Ave. Usage 180", "Ave. Usage 2013", "No. of Papers"]]),
            ("Citations Per Countries",
             sorted(self.data_obj['country_vs_citation_averages'].items(), key=lambda x: x[1]['average'], reverse=True),
             [["Country", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Unique Country",
             sorted(self.data_obj['unique_country_vs_citation_averages'].items(), key=lambda x: x[0], reverse=True),
             [["Unique Countries", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Length",
             sorted(self.data_obj['length_vs_citation_averages'].items(), key=lambda x: x[0], reverse=True),
             [["Length (Pages)", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per References",
             sorted(self.data_obj['references_vs_citation_averages'].items(), key=lambda x: x[0], reverse=True),
             [["No. of References", "Ave. Citations", "No. of Papers"]]),
            ("Affiliations vs Year", sorted(self.data_obj['affiliations_vs_year_dict'].items()),
             [["Year", "Affiliation %", "Total Papers"]])
        ]

        # Iterate through the list of results and write each one to a different Excel sheet
        for sheet_name, content, headers in results:
            # Create a list to store the table data
            table = headers

            # Add data rows to the table
            for key, row_data in content:
                row = [key] + list(row_data.values())  # Combine key and data values into one row
                table.append(row)

            # Convert the table to a DataFrame
            df = pd.DataFrame(table[1:], columns=table[0])

            # Write the DataFrame to the Excel file in the specified sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    sys.stdout = open('results_file.txt', 'w')
    rt.print_results()
    print()
    print("Results written to 'results.xlsx'")


print_results(rt)
