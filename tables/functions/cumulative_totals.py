from django.core.files.base import ContentFile
import pandas as pd
import os
import ast
import re

# Convert string representation of dictionaries to actual dictionaries
def convert_to_dict(value):
    try:
        return ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return {}

# Function to sum dictionaries
def sum_dictionaries(dicts):
    sum_dict = {}
    for d in dicts:
        for key, value in d.items():
            sum_dict[key] = sum_dict.get(key, 0) + value
    return sum_dict


def convert_to_double_quotes(d):
    return str(d).replace("'", '"')

def compute_cumulative(grantee, at_directory):
    # Get all CSV files in the directory
    csv_files = [file for file in os.listdir(at_directory) if file.startswith('dag_at')]
    
    # Create an empty list to store DataFrames for each CSV file
    dfs = []
    
    # Iterate through CSV files and read them into DataFrames
    for csv_file in csv_files:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(os.path.join(at_directory, csv_file))
        
        # Convert the code columns to dictionaries
        code_columns = df.columns[1:]
        for column in code_columns:
            df[column] = df[column].apply(convert_to_dict)
        
        # Append the DataFrame to the list
        dfs.append(df)
    
    # Combine all DataFrames in the list to calculate the sum of dictionaries
    combined_df = pd.concat(dfs)
    
    # Group by "district" and sum the dictionaries for each group
    sum_df = combined_df.groupby("district").agg(lambda x: sum_dictionaries(x)).reset_index()
    
    for col in sum_df.columns[1:]:
        sum_df[col] = sum_df[col].apply(convert_to_double_quotes)
    
    # Extract years from filenames
    years = [int(re.findall(r'\d{4}', file)[0]) for file in csv_files]
    
    # Find the minimum and maximum years
    min_year = min(years)
    max_year = max(years)
    
    # Generate the new filename
    last_year = int(re.search(r'(\d{4})\d{4}', csv_files[-1]).group(1)) + 1
    years.append(last_year)
    
    # Save the resulting DataFrame to a CSV file
    return ContentFile(sum_df.to_csv(index=False))
    

