import os
import pandas as pd
import re
import json
import warnings
from django.core.files.base import ContentFile
warnings.simplefilter(action='ignore', category=pd.errors.PerformanceWarning)

# Function to drop specific entries in the JSON
def drop_specific_entries(json_data, entries_to_drop):
    try:
        # Load the JSON data
        data = json.loads(json_data)
    except (json.JSONDecodeError, TypeError):
        # Handle invalid JSON or non-string data
        return json_data
    
    # Drop the specified entries
    for entry in entries_to_drop:
        if entry in data:
            del data[entry]
    
    # Convert the modified JSON back to a string
    return json.dumps(data)

# Function to add CummulativeTotal to each JSON
def add_annual_total(json_str):
    data_dict = json.loads(json_str)
    data_dict['CummulativeTotal'] = sum(data_dict.get(f'AnnualTotalY{i}', 0) for i in range(1, 50))
    return json.dumps(data_dict)
    

def compute_cumulative_totals(csv_directory, grantee):
    csv_files = [file for file in os.listdir(csv_directory) if file.startswith(f'AT_{grantee}_') and file.endswith('.csv')]
    
    # Sort the CSV files based on the ascending years
    sorted_csv_files = sorted(csv_files)
    
    # Read the CSV files into separate DataFrames
    dfs = []
    for i, csv_file in enumerate(sorted_csv_files, start=1):
        df = pd.read_csv(os.path.join(csv_directory, csv_file))
        globals()[f'df{i}'] = df
        dfs.append(df)
    
    columns_to_process = list(df.columns)
    
    # Specify the columns with JSON data and the entries to drop for each column
    entries_to_drop = ['TotalQ1', 'TotalQ2', 'TotalQ3', 'TotalQ4']
    
    # Apply the custom function to modify the JSON data for each specified column in dfs
    for df in dfs:
        for column in columns_to_process:
            df[column] = df[column].apply(lambda x: drop_specific_entries(x, entries_to_drop))
    
    # Concatenate the dataframes vertically
    combined_df = pd.concat(dfs, axis=0)
    
    # Reset the index of the combined dataframe
    combined_df = combined_df.reset_index(drop=True)
    
    # Create a new column 'level_1' to hold the column names
    combined_df['level_1'] = combined_df.groupby('district').cumcount() + 1
    combined_df['level_1'] = 'AnnualTotal' + combined_df['level_1'].astype(str)
    
    # Pivot the dataframe to have the desired format
    merged_df = combined_df.pivot(index='district', columns='level_1').reset_index()
    
    # Flatten the multi-level column index
    merged_df.columns = merged_df.columns.map('_'.join)
    df = merged_df
    
    # Create a new DataFrame by grouping columns with similar prefixes
    new_df = pd.DataFrame()
    for column in df.columns:
        prefix = column.split('_')[0]
        if prefix not in new_df.columns:
            new_df[prefix] = df[column]
        else:
            new_df[prefix] = new_df[prefix] + df[column]
    
    # Assuming 'new_df' is your DataFrame
    
    # Create a copy of the DataFrame
    df = new_df.copy()
    
    # Convert column names to strings
    df.columns = df.columns.astype(str)
    
    # Exclude the first row from the operation
    for col in df.columns:
        if col != 'district':  # Exclude 'district' column
            df[col] = df[col].apply(lambda x: re.findall(r'\d+', str(x))).apply(lambda x: {"AnnualTotal": list(map(int, x))})
    
    # Assuming df is your DataFrame
    # Create a copy of the DataFrame to avoid modifying the original
    df = df.copy()
    
    # Convert column names to strings
    df.columns = df.columns.astype(str)
    
    # Convert the columns excluding 'District'
    for col in df.columns:
        if col != 'district':
            df[col] = df[col].apply(lambda x: re.findall(r'\d+', str(x))).apply(lambda x: {"AnnualTotalY{}".format(i+1): int(val) for i, val in enumerate(x)})
    # Convert all columns except 'District' to JSON in each cell
    df_json = df.drop('district', axis=1).applymap(json.dumps)
    
    # Add the 'District' column back to the DataFrame at the beginning
    df_json = pd.concat([df['district'], df_json], axis=1)
    
    
    
    # Apply the function to each column
    df_json.iloc[:, 1:] = df_json.iloc[:, 1:].applymap(add_annual_total)
    # Extract years from filenames
    years = [int(re.search(r'(\d{4})\d{4}', file).group(1)) for file in csv_files]
    
    # Add the last year based on the assumption that the last file name contains the end year
    last_year = int(re.search(r'(\d{4})\d{4}', csv_files[-1]).group(1)) + 1
    years.append(last_year)
    
    # Create the filename with the constant prefix and grantee name, followed by the smallest and largest years, in small letters
    return ContentFile(df_json.to_csv(index=False))




