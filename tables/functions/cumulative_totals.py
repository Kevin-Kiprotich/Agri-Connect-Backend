from django.core.files.base import ContentFile
import os
import re
import pandas as pd
import ast
import json

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


# Group files by consecutive cumulative totals
def group_files_by_cumulative_totals(at_directory):
    print(at_directory)
    cumulative_total_groups = {}  # Dictionary to store files grouped by consecutive cumulative totals
    csv_files = sorted([file for file in os.listdir(at_directory) if file.startswith('dag_at')])

    cumulative_files = []  # To store files progressively
    if csv_files:
        first_match = re.search(r'_(\d{4})(\d{2})', csv_files[0])
        if first_match:
            start_year = first_match.group(1)
            end_year = int(start_year)  # Initialize end_year with start_year

    for file in csv_files:
        # Extract the year from the filename
        match = re.search(r'_(\d{4})(\d{2})', file)
        if match:
            current_file_year = match.group(1)
            end_year += 1  # Increment end year for each file

            # Define group key with incremented end year
            group_key = f"{start_year}{end_year}"

            # Add the current file to the cumulative files list
            cumulative_files.append(file)

            # Store the cumulative files in the group
            cumulative_total_groups[group_key] = cumulative_files.copy()  # Use copy to avoid reference issues

    return cumulative_total_groups

# Function to compute cumulative totals
def compute_progressive_cumulative_totals(at_directory, grantee):
    # Group files by year ranges
    print(at_directory)
    cumulative_groups = group_files_by_cumulative_totals(at_directory)
    dfs_by_group = {}

    for group_key, csv_files in cumulative_groups.items():
        dfs = []
        
        # Load each file in the current group
        for csv_file in csv_files:
            df = pd.read_csv(os.path.join(at_directory, csv_file))
            code_columns = df.columns[1:]  # Skip the 'district' column

            # Convert code columns to dictionaries
            for column in code_columns:
                df[column] = df[column].apply(convert_to_dict)
            dfs.append(df)

        # Combine and sum dictionaries for cumulative group
        combined_df = pd.concat(dfs)
        sum_df = combined_df.groupby("district").agg(lambda x: sum_dictionaries(x)).reset_index()
        
        # Convert dictionary columns to JSON string format
        for col in sum_df.columns[1:]:
            sum_df[col] = sum_df[col].apply(json.dumps)
        
        # Save each cumulative total result as CSV
        cumulative_totals_path = f"dag_ct_{grantee}_{group_key}.csv"
          # Store in dictionary if needed for further use

        return group_key, ContentFile(sum_df.to_csv(index=False))
    