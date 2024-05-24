import matplotlib.pyplot as plt
from pathlib import Path
import json

# TODO - change axis font size

# Define the directory to save the plots
plot_save_directory = Path("plots")

# Create the directory if it doesn't exist
plot_save_directory.mkdir(parents=True, exist_ok=True)

# Load data from the specified JSON file path
def load_json_data(json_file_path):
    data = {}
    if Path(json_file_path).is_file():
        try:
            # Open the JSON file and load its contents as a dictionary
            with open(json_file_path, 'r') as file:
                data = json.load(file)
        except json.JSONDecodeError as e:
            print(f"Error loading JSON data: {e}")
    else:
        print(f"JSON file not found: {json_file_path}")
    return data


# Function to plot a line graph with average values and number of papers and save it to a file
def plot_line_graph(data, y_label, x_label, plot_name):
    # Convert and sort data based on integer keys
    sorted_data = sorted(data.items(), key=lambda item: int(item[0]))

    # Prepare lists for x_values, averages, and number of papers
    x_values = []
    averages = []
    no_of_papers = []

    # Filter data and populate lists
    for key, value in sorted_data:
        # Convert key to int
        int_key = int(key)
        # Extract 'papers' and check if greater than 75
        papers = value.get('papers', 1001)
        if papers > 1001:
            x_values.append(int_key)
            averages.append(value.get('average', 0))
            no_of_papers.append(papers)

    # Check if there are any data points to plot
    if not x_values:
        print("No data points to plot. All entries have 1001 or fewer papers.")
        return

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 6))
    ax1.plot(x_values, averages, marker='o', label=y_label, color='blue')
    ax1.set_xlabel(x_label)
    ax1.set_ylabel(y_label, color='blue')
    ax1.tick_params(axis='y', labelcolor='blue')

    # Secondary y-axis for number of papers
    ax2 = ax1.twinx()
    ax2.bar(x_values, no_of_papers, color='orange', alpha=0.5, label='Number of Papers')
    ax2.set_ylabel('Number of Papers', color='orange')
    ax2.tick_params(axis='y', labelcolor='orange')

    # Customize plot appearance
    ax1.set_ylim(0, max(averages) * 1.1)
    ax2.set_ylim(0, max(no_of_papers) * 1.1)
    ax1.set_xlim(x_values[0], x_values[-1])
    ax2.set_xlim(x_values[0], x_values[-1])
    fig.suptitle(f'{y_label} per {x_label}')
    fig.legend(loc='upper left')
    plt.xticks(rotation='vertical', ha='right')
    ax1.grid(True)

    # Save the plot to a file
    plot_file_path = plot_save_directory / f"{plot_name}.png"
    plt.savefig(plot_file_path)
    print(f"Saved plot to {plot_file_path}")

    # Close the plot to free memory
    plt.close(fig)


# Function to plot affiliation percentage vs. year and save it to a file
def plot_affiliation_percentage_vs_year(affiliations_vs_year_dict):
    # Extract and sort the keys (years)
    years = sorted(affiliations_vs_year_dict.keys())

    # Calculate the total counts and percentages
    percentages = []
    for year in years:
        year_data = affiliations_vs_year_dict[year]
        true_count = year_data.get('True', 0)
        false_count = year_data.get('False', 0)
        total_count = true_count + false_count

        # Calculate the affiliation percentage
        if total_count > 0:
            percentage = (true_count / total_count) * 100
        else:
            percentage = 0

        percentages.append(percentage)

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, percentages, marker='o', color='blue', label='Affiliation Percentage')

    # Add labels and title
    plt.xlabel('Year')
    plt.ylabel('Affiliation Percentage (%)', color="blue")
    plt.title('Affiliation Percentage vs. Year\n\n')

    plt.legend(loc='upper left')
    plt.tick_params(axis='y', labelcolor='blue')

    # Add grid
    plt.grid(True)

    # Adjust the x-axis range and labels
    plt.xlim(years[0], years[-1])

    # Customize the x-axis labels
    if len(years) > 10:
        year_interval = max(1, len(years) // 10)
        plt.xticks(years[::year_interval])
    else:
        plt.xticks(years)

    # Add legend and rotate x-axis labels for better readability
    plt.legend(loc='upper left')
    plt.xticks(rotation='vertical')

    # Save the plot to a file
    plot_file_path = plot_save_directory / "affiliation_percentage_vs_year.png"
    plt.savefig(plot_file_path)
    plt.show()
    print(f"Saved plot to {plot_file_path}")

    # Close the plot to free memory
    plt.close()


# Function to plot average citations vs. funding type and save it to a file
def plot_funding_bar_graph(data):
    # Extract the categories, average citations, and number of papers from the data
    categories = list(data.keys())
    averages = [data[category]['average'] for category in categories]
    papers = [data[category]['papers'] for category in categories]

    # Define bar width and positions for bars
    bar_width = 0.35
    index = range(len(categories))

    # Create the plot
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot average citations as bars
    ax1.bar(index, averages, width=bar_width, color='#4e79a7', alpha=0.7, label='Average Citations')
    ax1.set_ylabel('Average Citations', color='#4e79a7')
    ax1.tick_params(axis='y', labelcolor='#4e79a7')

    # Create a secondary y-axis for number of papers
    ax2 = ax1.twinx()

    # Plot number of papers as bars, staggered by bar width
    ax2.bar([i + bar_width for i in index], papers, width=bar_width, color='#f28e2b', alpha=0.7,
            label='Number of Papers')
    ax2.set_ylabel('Number of Papers', color='#f28e2b')
    ax2.tick_params(axis='y', labelcolor='#f28e2b')

    # Customize the plot
    ax1.set_xlabel('Funding Status')
    ax1.set_xticks([i + bar_width / 2 for i in index])
    ax1.set_xticklabels(categories)
    ax1.grid(True, axis='y', linestyle='--', alpha=0.6)
    fig.suptitle('Average Citations and Number of Papers by Funding Status')
    fig.legend(loc='upper left')
    plt.xticks(rotation='vertical')

    # Save the plot to a file
    plot_file_path = plot_save_directory / "avg_citations_vs_funding.png"
    plt.savefig(plot_file_path)
    print(f"Saved plot to {plot_file_path}")

    # Close the plot to free memory
    plt.close(fig)


# Main function to load data and plot the required graphs
def main():
    # Define the JSON file path
    json_file_path = 'Results/All/results_data_obj.json'

    # Load JSON data from the specified file
    data = load_json_data(json_file_path)

    # Check if data was loaded successfully
    if not data:
        print("No data loaded. Exiting.")
        return

    # Define datasets for plotting
    datasets = [
        [data['citations_per_year_averages'], 'Average Citations', 'Year', 'citations_per_year_averages'],
        [data['authors_vs_citations_averages'], 'Average Citations', 'No. of Authors', 'authors_vs_citations_averages'],
        [data['keywords_vs_citations_averages'], 'Average Citations', 'No. of Keywords', 'keywords_vs_citations_averages'],
        [data['unique_country_vs_citation_averages'], 'Average Citations', 'No. of Unique Author Countries', 'unique_country_vs_citation_averages'],
        [data['length_vs_citation_averages'], 'Average Citations', 'Paper Length', 'length_vs_citation_averages'],
        [data['references_vs_citation_averages'], 'Average Citations', 'Number of References', 'references_vs_citation_averages'],
    ]

    # Iterate over datasets and plot line graphs
    for dataset in datasets:
        plot_line_graph(dataset[0], dataset[1], dataset[2], dataset[3])

    # Plot affiliation percentage vs. year
    plot_affiliation_percentage_vs_year(data['affiliations_vs_year_dict'])

    # Plot average citations vs. funding type
    plot_funding_bar_graph(data['funding_orgs_vs_citations_averages'])


# Execute the main function
if __name__ == "__main__":
    main()
