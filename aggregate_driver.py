import sys
import pandas as pd
import json
from research_topics import ResearchTopics

# Specify the path to your JSON file
elsevier_json_file_path = 'Results/elsevier_data_obj.json'
springer_json_file_path = 'Results/springer_data_obj.json'
tandf_json_file_path = 'Results/tandf_data_obj.json'
wiley_json_file_path = 'Results/wiley_data_obj.json'


with open(elsevier_json_file_path, 'r') as file:
    elsevier_data_obj = json.load(file)

with open(springer_json_file_path, 'r') as file:
    springer_data_obj = json.load(file)

with open(tandf_json_file_path, 'r') as file:
    tandf_data_obj = json.load(file)

with open(wiley_json_file_path, 'r') as file:
    wiley_data_obj = json.load(file)

data_obj = {}
json_list = [elsevier_data_obj, springer_data_obj, tandf_data_obj, wiley_data_obj]

topics = ["citations_per_year_averages", "authors_vs_citations_averages", "keywords_vs_citations_averages",
          "journals_vs_citations_averages", "journals_vs_references_averages", "doctype_vs_citations_averages",
          "doctype_vs_references_averages", "doctype_vs_references_averages", "publisher_vs_citations_averages",
          "publisher_vs_references_averages", "city_vs_citations_averages", "funding_orgs_vs_citations_averages",
          "country_vs_citation_averages", "unique_country_vs_citation_averages", "length_vs_citation_averages",
          "references_vs_citation_averages"]

topic_other = "citations_vs_research_areas_averages"
topic_other2 = "affiliations_vs_year_dict"

# Initialise keys in dictionary
for t in topics:
    data_obj[t] = {}

data_obj[topic_other] = {}
data_obj[topic_other2] = {}
data_obj["total_papers"] = 0

for json_obj in json_list:
    data_obj["total_papers"] += json_obj["total_papers"]

    for topic in topics:
        for key, values in json_obj[topic].items():
            if key not in data_obj[topic]:
                data_obj[topic][key] = {
                    "average": values["average"],
                    "papers": values["papers"]
                }
            else:
                init_ave = data_obj[topic][key]['average']
                init_papers = data_obj[topic][key]['papers']

                new_ave = values['average']
                new_papers = values['papers']

                combined_papers = init_papers + new_papers
                combined_ave = ((init_papers * init_ave) + (new_papers * new_ave)) / combined_papers

                data_obj[topic][key]["average"] = combined_ave
                data_obj[topic][key]["papers"] = combined_papers

    for key, values in json_obj[topic_other].items():
        if key not in data_obj[topic_other]:
            data_obj[topic_other][key] = {
                "avg_citations": values["avg_citations"],
                "avg_usage_180": values["avg_usage_180"],
                "avg_usage_2013": values["avg_usage_2013"],
                "no_papers": values["no_papers"]
            }
        else:
            init_papers = data_obj[topic_other][key]["no_papers"]
            new_papers = values["no_papers"]
            combined_papers = init_papers + new_papers

            init_ave_cit = data_obj[topic_other][key]['avg_citations']
            init_ave_180 = data_obj[topic_other][key]['avg_usage_180']
            init_ave_2013 = data_obj[topic_other][key]['avg_usage_2013']

            new_ave_cit = values['avg_citations']
            new_ave_180 = values['avg_usage_180']
            new_ave_2013 = values['avg_usage_2013']

            data_obj[topic_other][key]["avg_citations"] = \
                ((init_papers * init_ave_cit) +
                 (new_papers * new_ave_cit)) / combined_papers

            data_obj[topic_other][key]["avg_usage_180"] = \
                ((init_papers * init_ave_180) +
                 (new_papers * new_ave_180)) / combined_papers

            data_obj[topic_other][key]["avg_usage_2013"] = \
                ((init_papers * init_ave_2013) +
                 (new_papers * new_ave_2013)) / combined_papers

            data_obj[topic_other][key]["no_papers"] = combined_papers

    for key, values in json_obj[topic_other2].items():
        if key not in data_obj[topic_other2]:
            data_obj[topic_other2][key] = {
                "False": values["False"],
                "True": values["True"]
            }
        else:
            data_obj[topic_other2][key]["True"] += values["True"]
            data_obj[topic_other2][key]["False"] += values["False"]


def print_results(self):
    # Open an Excel file using pandas.ExcelWriter
    with pd.ExcelWriter('results.xlsx') as writer:
        # Define each sheet name and the respective list of data
        results = [
            ("Citations Per Year",
             sorted(self.data_obj['citations_per_year_averages'].items(), key=lambda x: int(x[0])),
             [["Publish Year", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Authors",
             sorted(self.data_obj['authors_vs_citations_averages'].items(), key=lambda x: int(x[0])),
             [["No. of Authors", "Ave. Citations", "No. of Papers"]]),
            ("Citations Per Keywords",
             sorted(self.data_obj['keywords_vs_citations_averages'].items(), key=lambda x: int(x[0])),
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
            ("Affiliations vs Year",
             sorted(self.data_obj['affiliations_vs_year_dict'].items(), key=lambda x: int(x[0])),
             [["Year", "Affiliation %", "Total Papers"]])
        ]

        # Iterate through the list of results and write each one to a different Excel sheet
        for sheet_name, content, headers in results:
            # Create a list to store the table data
            table = headers

            # Add data rows to the table
            if sheet_name == "Affiliations vs Year":
                for year, citations in content:
                    # Calculate the total number of True and False values
                    total_references = citations.get('True', 0) + citations.get('False', 0)

                    # Calculate the percentage of True values
                    if total_references > 0:
                        affiliation_percentage = (citations.get('True', 0) / total_references) * 100
                    else:
                        affiliation_percentage = 0

                    # Append the year, affiliation percentage, and total references to the table
                    table.append([year, f"{affiliation_percentage:.2f}%", total_references])
            else:
                # For other sheets, add data as-is
                for key1, row_data in content:
                    row1 = [key1] + list(row_data.values())
                    table.append(row1)

            # Convert the table to a DataFrame
            df = pd.DataFrame(table[1:], columns=table[0])

            # Write the DataFrame to the Excel file in the specified sheet
            df.to_excel(writer, sheet_name=sheet_name, index=False)

    sys.stdout = open('results_file.txt', 'w')
    rt.print_results()


with open('results_data_obj.json', 'w') as results_file:
    json.dump(data_obj, results_file)

rt = ResearchTopics({}, data_obj)
print_results(rt)
