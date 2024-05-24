import re
import pandas as pd

# Load the Excel file
springer_xls = pd.ExcelFile('springer_data.xlsx')
springer_df = springer_xls.parse(springer_xls.sheet_names[0])


# Define the function to refactor the type
def refactor_type(text):
    # If the input is not a string, convert it to a string
    if not isinstance(text, str):
        text = str(text)

    # Add a space before each word with a capital letter (except the first word)
    new_text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    return new_text


# Define a function to remove everything after the year
def refactor_journal(text):
    # Use a regular expression to find the year (four-digit number) and everything that follows
    new_text = re.sub(r'\d{4}.*$', '', text)
    return new_text


def transform_string(input_str):
    # Split the input string by commas and strip leading/trailing whitespaces
    names = [name.strip() for name in input_str.split(',')]

    # Initialize an empty list to hold the modified pairs
    modified_pairs = []

    # Iterate through the list in pairs
    for i in range(0, len(names), 2):
        # If there is a next name, create a pair wrapped in double quotes
        if i + 1 < len(names):
            pair = f'"{names[i]} {names[i + 1]}"'
            modified_pairs.append(pair)

    # Join the modified pairs with semicolon and space separator
    result_str = '; '.join(modified_pairs)

    # Surround the final result with square brackets
    final_result = f"[{result_str}]"

    return final_result


def string_to_list(input_str):
    # Remove the surrounding square brackets
    input_str = input_str.strip("[]")

    # Split the string by semicolons to get each element
    elements = input_str.split(';')

    # Strip leading and trailing whitespaces and double quotes from each element
    elements = [element.strip().strip('"') for element in elements]

    return elements

# Specify the column name containing the wos_doi values
# Specify the column name to modify
column_name = 'authors'  # Replace 'authors' with the name of the column you want to modify

# Apply the transformation function to the specified column
springer_df = springer_df[springer_df[column_name].str.endswith(']')]

# Save the modified DataFrame back to the Excel file
springer_df.to_excel('springer_data.xlsx', index=False, sheet_name=springer_xls.sheet_names[0])
