import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd
from pandas import *
from datetime import datetime

"""
REFERENCES
- wrong/missing references
    - over time
    - journal/publisher/ranking/publication type

KEYWORDS
- use abstracts and titles
    - categorise
    - inconsistencies with WoS

TIMING
- time between submission and acceptance
    - over time
    - dependent on time/ranking etc.

CITATIONS
    - effect of comments
    - retracted papers
"""
# TODO - add sd to graph

# Convert data to dictionaries
elsevier_xls = ExcelFile('elsevier_data.xlsx')
elsevier_df = elsevier_xls.parse(elsevier_xls.sheet_names[0])

tandf_xls = ExcelFile('tandf_data.xlsx')
tandf_df = tandf_xls.parse(tandf_xls.sheet_names[0])

wiley_xls = ExcelFile('wiley_data.xlsx')
wiley_df = wiley_xls.parse(wiley_xls.sheet_names[0])

# wos_tandf_xls = ExcelFile('tandf_wos_data.xlsx')
# wos_tandf_df = wos_tandf_xls.parse(wos_tandf_xls.sheet_names[0])

"""
TIMING
- correctness between WoS and Publisher
- average times
"""


# Function to calculate the time difference in days
def calculate_time_difference(date1, date2):
    date1_str = date1.strftime('%d-%m-%Y')
    date2_str = date2.strftime('%d-%m-%Y')
    delta = datetime.strptime(date2_str, '%d-%m-%Y') - datetime.strptime(date1_str, '%d-%m-%Y')
    return abs(delta.days)


timing_dict = defaultdict(lambda: {
    "ave_rec2acc": [],
    "ave_acc2pub": [],
    "ave_rec2pub": []
})


def average_publish_time(publisher_database, publisher):
    # Dictionary to hold the average time differences
    timing_dict = defaultdict(lambda: {"ave_rec2acc": []})

    # Calculate average times for each publication year
    for index, paper in publisher_database.iterrows():
        rec_date = paper["received_date"]
        acc_date = paper["accepted_date"]
        rec_year = rec_date.year

        # Handle missing publication year
        if pd.isna(rec_year):
            continue

        if not pd.isna(rec_date) and not pd.isna(acc_date):
            rec_acc_diff = calculate_time_difference(rec_date, acc_date)
            timing_dict[rec_year]["ave_rec2acc"].append(rec_acc_diff)

    # Calculate averages and standard deviations
    years = []
    rec_acc_avgs = []
    rec_acc_stds = []

    for year, times in timing_dict.items():
        if len(times["ave_rec2acc"]) == 0:
            continue

        years.append(year)

        # Calculate average and standard deviation
        rec_acc_avg = np.mean(times["ave_rec2acc"])
        rec_acc_std = np.std(times["ave_rec2acc"])

        rec_acc_avgs.append(rec_acc_avg)
        rec_acc_stds.append(rec_acc_std)

    # Sort data by year
    years, rec_acc_avgs, rec_acc_stds = zip(*sorted(zip(years, rec_acc_avgs, rec_acc_stds)))

    # Plotting
    plt.figure(figsize=(10, 6))

    # Plot average received to accepted time
    plt.plot(years, rec_acc_avgs, marker='o', label='Average Received to Accepted Date')

    # Plot standard deviation for the same data as its own line
    plt.plot(years, rec_acc_stds, marker='o', linestyle='--', color='red', label='Standard Deviation')

    # Labels and title
    plt.xlabel('Received Year')
    plt.ylabel('Time (days)')
    plt.title(f'{publisher} - Average Received to Accepted Time and Standard Deviation')
    plt.legend()
    plt.grid(True)

    # Rotate x-axis labels to vertical
    plt.xticks(rotation='vertical')

average_publish_time(tandf_df, 'tandf')
average_publish_time(elsevier_df, 'elsevier')
plt.show()
