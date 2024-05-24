import sys
import matplotlib.pyplot as plt
from pandas import *
from research_topics import ResearchTopics

wos_elsevier_xls = ExcelFile('elsevier_wos_data.xlsx')
wos_elsevier_df = wos_elsevier_xls.parse(wos_elsevier_xls.sheet_names[0])

wos_df = wos_elsevier_df

rt = ResearchTopics(wos_df)


def line_graph(data_dict, ave_dict, y_label, x_label):
    # Sort data by year
    sorted_averages = sorted(ave_dict.items(), key=lambda x: x[0])
    x_value, averages = zip(*sorted_averages)
    no_of_papers = [len(data_dict[x]) for x in x_value]

    # Create a figure and a set of subplots
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot average citations on the primary y-axis
    ax1.plot(x_value, averages, marker='o', label=y_label, color='blue')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Create a secondary y-axis to plot number of papers
    ax2 = ax1.twinx()
    ax2.bar(x_value, no_of_papers, color='orange', alpha=0.5, label='Number of Papers')
    ax2.set_ylabel('Number of Papers', color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Set both y-axes to start at zero
    ax1.set_ylim(0, max(averages) * 1.1)
    ax2.set_ylim(0, max(no_of_papers) * 1.1)

    # Set x-axis to include all data points and extend to the rightmost point
    ax1.set_xlim(x_value[0], x_value[-1])
    ax2.set_xlim(x_value[0], x_value[-1])

    # Title and legend
    fig.suptitle(f'{y_label} per {x_label}')
    fig.legend(loc='upper left')

    # Rotate x-axis labels to vertical, similar to the initial example
    plt.xticks(rotation='vertical', ha='right')

    # Add grid for the primary y-axis
    ax1.grid(True)


def plot_affiliation_percentage_vs_year(affiliations_vs_year_dict):
    # Initialize lists to hold years and affiliation percentages
    years = []
    affiliation_percentages = []

    # Iterate through the sorted dictionary items by year
    for year, citations in sorted(affiliations_vs_year_dict.items()):
        # Calculate the total number of True and False values
        total_references = citations.get('True', 0) + citations.get('False', 0)
        # Calculate the percentage of True values
        if total_references > 0:
            affiliation_percentage = (citations.get('True', 0) / total_references) * 100
        else:
            affiliation_percentage = 0

        # Append year and affiliation percentage to respective lists
        years.append(year)
        affiliation_percentages.append(affiliation_percentage)

    # Plotting
    plt.figure(figsize=(10, 6))

    # Plot the line graph with markers for each data point
    plt.plot(years, affiliation_percentages, marker='o', linestyle='-', color='#4e79a7', label='Affiliation Percentage')

    # Set labels and title
    plt.xlabel('Year')
    plt.ylabel('Affiliation Percentage (%)')
    plt.title('Affiliation Percentage vs. Year')

    # Add grid for better readability
    plt.grid(True)

    # Set the x-axis range to start at the first year and end at the last year
    plt.xlim(years[0], years[-1])

    # Customize the x-axis ticks to display only a subset of years
    # Calculate the number of years between each label based on the range of data
    num_years = len(years)
    # Display labels at intervals (e.g., every 5 years)
    if num_years > 10:
        year_interval = max(1, num_years // 10)  # Adjust the interval as needed
        plt.xticks(years[::year_interval])

    # Add a legend
    plt.legend(loc='upper left')

    # Rotate x-axis labels for better readability
    plt.xticks(rotation='vertical')


def graph_average_citations_vs_funding(data_dict, ave_dict):
    # Sort the data by average citations
    sorted_averages = sorted(ave_dict.items(), key=lambda x: x[1])
    funding_types, averages = zip(*sorted_averages)
    no_of_papers = [len(data_dict[funding]) for funding in funding_types]

    # Create a figure and axes
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Define the width of the bars
    bar_width = 0.35

    # Plot average citations as bars on the primary y-axis
    ax1.bar(funding_types, averages, width=bar_width, label='Average Citations', color='#4e79a7', alpha=0.7)

    # Create a secondary y-axis to plot the number of papers as bars
    ax2 = ax1.twinx()
    ax2.bar([x + bar_width for x in range(len(funding_types))], no_of_papers, width=bar_width, label='Number of Papers', color='#f28e2b', alpha=0.7)

    # Set y-axis labels
    ax1.set_ylabel('Average Citations', color='#4e79a7')
    ax2.set_ylabel('Number of Papers', color='#f28e2b')

    # Set y-axis limits and x-axis labels
    ax1.set_ylim(0, max(averages) * 1.2)
    ax2.set_ylim(0, max(no_of_papers) * 1.2)
    ax1.set_xlabel('Funding Type')
    ax1.set_xticks([x + bar_width / 2 for x in range(len(funding_types))])
    ax1.set_xticklabels(funding_types)

    # Add grid to the primary y-axis
    ax1.grid(True, axis='y', linestyle='--', alpha=0.6)

    # Add legend
    fig.legend(loc='upper left')

    # Set title
    fig.suptitle('Average Citations and Number of Papers by Funding Type')

    # Rotate x-axis labels for readability
    plt.xticks(rotation='vertical')


# Dataset list containing parameters for the function
dataset = [
    [rt.citations_per_year_dict, rt.citations_vs_pubyear_averages, 'Average Citations', 'Year'],
    [rt.authors_vs_citations_dict, rt.authors_vs_citations_averages, 'Average Citations', 'No. of Authors'],
    [rt.keywords_vs_citations_dict, rt.keywords_vs_citations_averages, 'Average Citations', 'No. of Keywords'],
    [rt.unique_country_vs_citation_dict, rt.unique_country_vs_citation_averages, 'Average Citations', 'No. of Unique Author Countries'],
    [rt.length_vs_citation_dict, rt.length_vs_citation_averages, 'Average Citations', 'Paper Length'],
    [rt.references_vs_citation_dict, rt.references_vs_citation_averages, 'Average Citations', 'Average References']
]

# Iterate over the dataset and call the function for each set of parameters
for data in dataset:
    line_graph(data[0], data[1], data[2], data[3])

plot_affiliation_percentage_vs_year(rt.affiliations_vs_year_dict)
graph_average_citations_vs_funding(rt.funding_orgs_vs_citations_dict, rt.funding_orgs_vs_citations_averages)

# Print tables to console
sys.stdout = open('results_file.txt', 'w')
rt.print_results()

# Show the plot
plt.show()
