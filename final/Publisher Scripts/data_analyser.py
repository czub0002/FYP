# Import necessary libraries
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from datetime import datetime
import pandas as pd
from pandas import ExcelFile


# Define function to calculate time difference in days
def calculate_time_difference(date1, date2):
    # Calculate absolute time difference in days
    return abs((date2 - date1).days)


# Function to calculate received-to-accepted time differences
def calculate_time_differences(database):
    # Dictionary to hold time differences by year
    timing_dict = defaultdict(list)

    # Process data to calculate the time difference for each year
    for index, paper in database.iterrows():
        rec_date = paper["received_date"]
        acc_date = paper["accepted_date"]

        # Skip rows with missing dates
        if pd.isna(rec_date) or pd.isna(acc_date):
            continue

        # Calculate time difference
        rec_acc_diff = calculate_time_difference(rec_date, acc_date)
        rec_year = rec_date.year

        # Store the time difference for the given year
        timing_dict[rec_year].append(rec_acc_diff)

    return timing_dict


# Function to calculate average and standard deviation for each year
def calculate_average_and_sd(timing_dict):
    # Lists to store years, averages, and standard deviations
    years = []
    averages = []
    sds = []

    # Calculate averages and SDs for each year
    for year, time_diffs in timing_dict.items():
        if len(time_diffs) == 0:
            continue

        # Calculate average and SD for the current year
        avg = np.mean(time_diffs)
        sd = np.std(time_diffs)

        years.append(year)
        averages.append(avg)
        sds.append(sd)

    # Sort data by year
    years, averages, sds = zip(*sorted(zip(years, averages, sds)))

    return years, averages, sds


# Load data from Excel files
elsevier_xls = ExcelFile('elsevier_data.xlsx')
elsevier_df = elsevier_xls.parse(elsevier_xls.sheet_names[0])

tandf_xls = ExcelFile('tandf_data.xlsx')
tandf_df = tandf_xls.parse(tandf_xls.sheet_names[0])

# Calculate time differences for Elsevier and T&F data
elsevier_time_differences = calculate_time_differences(elsevier_df)
tandf_time_differences = calculate_time_differences(tandf_df)

# Calculate averages and SDs for Elsevier and T&F data
years_elsevier, averages_elsevier, sds_elsevier = calculate_average_and_sd(elsevier_time_differences)
years_tandf, averages_tandf, sds_tandf = calculate_average_and_sd(tandf_time_differences)

# Combine data from Elsevier and T&F to calculate combined averages and SDs
combined_timing_dict = defaultdict(list)

# Combine data based on years
for year, time_diffs in elsevier_time_differences.items():
    combined_timing_dict[year].extend(time_diffs)

for year, time_diffs in tandf_time_differences.items():
    combined_timing_dict[year].extend(time_diffs)

# Calculate combined averages and SDs
combined_years, combined_averages, combined_sds = calculate_average_and_sd(combined_timing_dict)

# Create and save plots

# Elsevier plot
plt.figure(figsize=(10, 6))
plt.plot(years_elsevier, averages_elsevier, marker='o', linestyle='-', color='blue', label='Average')
plt.plot(years_elsevier, sds_elsevier, linestyle='--', color='red', label='Standard Deviation')
plt.title('Elsevier - Average Received to Accepted Time and Standard Deviation')
plt.xlabel('Received Year')
plt.ylabel('Time (days)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.savefig('elsevier_average_sd.png')  # Save the plot to a file
plt.close()  # Close the figure after saving

# T&F plot
plt.figure(figsize=(10, 6))
plt.plot(years_tandf, averages_tandf, marker='o', linestyle='-', color='orange', label='Average')
plt.plot(years_tandf, sds_tandf, linestyle='--', color='red', label='Standard Deviation')
plt.title('T&F - Average Received to Accepted Time and Standard Deviation')
plt.xlabel('Received Year')
plt.ylabel('Time (days)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.savefig('tandf_average_sd.png')  # Save the plot to a file
plt.close()  # Close the figure after saving

# Combined plot
plt.figure(figsize=(10, 6))
plt.plot(combined_years, combined_averages, marker='o', linestyle='-', color='green', label='Combined Average')
plt.plot(combined_years, combined_sds, linestyle='--', color='red', label='Standard Deviation')
plt.title('Combined Average Received to Accepted Time for Elsevier and T&F')
plt.xlabel('Received Year')
plt.ylabel('Time (days)')
plt.legend()
plt.grid(True)
plt.xticks(rotation=45)
plt.savefig('combined_average_sd.png')  # Save the plot to a file
plt.close()  # Close the figure after saving
