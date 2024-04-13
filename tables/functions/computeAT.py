import os
import pandas as pd
import json
import re
import warnings
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


def compute_annual_totals(quarters_path, grantee, startTime, endTime):
    # Generate the list of expected file names
    file_names = [
        # f"SUMS_{grantee}_JulDec_{yearStart}.csv",
        
        f"SUMS_{grantee}_JulSep_{startTime}.csv".casefold(),
        f"SUMS_{grantee}_OctDec_{startTime}.csv".casefold(),
        f"SUMS_{grantee}_JanMar_{endTime}.csv".casefold(),
        f"SUMS_{grantee}_AprJun_{endTime}.csv".casefold()
    ]
    
    # Get the list of CSV files in the directory
    csv_files = []
    for file in os.listdir(quarters_path):
        if file.endswith(".csv") and file in file_names:
            csv_files.append(os.path.join(quarters_path, file))
    
    # Assign CSV file paths to variables
    csvinput1 = ""
    csvinput2 = ""
    csvinput3 = ""
    csvinput4 = ""
    
    for csv_file in csv_files:
        if "JulDec".casefold() in csv_file:
            csvinput1 = csv_file
        elif "JulSep".casefold() in csv_file:
            csvinput1 = csv_file
        elif "OctDec".casefold() in csv_file:
            csvinput2 = csv_file
        elif "JanMar".casefold() in csv_file:
            csvinput3 = csv_file
        elif "AprJun".casefold() in csv_file:
            csvinput4 = csv_file

    # Read CSV files with pandas, skipping missing files
    try:
        df1 = pd.read_csv(csvinput1)
    except FileNotFoundError:
        df1 = None
    
    try:
        df2 = pd.read_csv(csvinput2)
    except FileNotFoundError:
        df2 = None
    
    try:
        df3 = pd.read_csv(csvinput3)
    except FileNotFoundError:
        df3 = None
    
    try:
        df4 = pd.read_csv(csvinput4)
    except FileNotFoundError:
        df4 = None
    dataframes = [df1, df2, df3, df4]
    
    columns_list  = None
    
    
    for df in dataframes:
        if df is not None:
            columns_list  = df.columns.tolist()
            break
            
    # Get the first row of the 'code11' column
    first_row_code11 = None
    
    for df in dataframes:
        if df is not None and 'code11' in df.columns:
            first_row_code11 = df.loc[0, 'code11']
            break
    
    
    
    # Specify the columns with JSON data and the entries to drop for each column
    columns_to_process = columns_list  # Add more columns as needed
    entries_to_drop = ['Adult_Male', 'Adult_Male', 'Youth_Male', 'Adult_Female', 'Reference', 'Youth_Female']
    
    
    
    # Apply the custom function to modify the JSON data for each specified column
    for column in columns_to_process:
        if df1 is not None:
            df1[column] = df1[column].apply(lambda x: drop_specific_entries(x, entries_to_drop))
        if df2 is not None:
            df2[column] = df2[column].apply(lambda x: drop_specific_entries(x, entries_to_drop))
        if df3 is not None:
            df3[column] = df3[column].apply(lambda x: drop_specific_entries(x, entries_to_drop))
        if df4 is not None:
            df4[column] = df4[column].apply(lambda x: drop_specific_entries(x, entries_to_drop))
    
    
    # Assuming you have four dataframes named df1, df2, df3, and df4
    
    # Concatenate the dataframes vertically
    combined_df = pd.concat([df1, df2, df3, df4], axis=0)
    
    # Reset the index of the combined dataframe
    combined_df = combined_df.reset_index(drop=True)
    
    # Create a new column 'level_1' to hold the column names
    combined_df['level_1'] = combined_df.groupby('district').cumcount() + 1
    combined_df['level_1'] = 'ReferenceQ' + combined_df['level_1'].astype(str)
    
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
            df[col] = df[col].apply(lambda x: re.findall(r'\d+', str(x))).apply(lambda x: {"Total": list(map(int, x))})
    
    
    # Assuming df is your DataFrame
    # Create a copy of the DataFrame to avoid modifying the original
    df = df.copy()
    
    # Convert column names to strings
    df.columns = df.columns.astype(str)
    
    # Convert the columns excluding 'District'
    for col in df.columns:
        if col != 'district':
            df[col] = df[col].apply(lambda x: re.findall(r'\d+', str(x))).apply(lambda x: {"TotalQ{}".format(i+1): int(val) for i, val in enumerate(x)})
    
    # Convert all columns except 'District' to JSON in each cell
    df_json = df.drop('district', axis=1).applymap(json.dumps)
    
    # Add the 'District' column back to the DataFrame at the beginning
    df_json = pd.concat([df['district'], df_json], axis=1)
    
    # Function to add AnnualTotal to each JSON
    def add_annual_total(json_str):
        data_dict = json.loads(json_str)
        data_dict['AnnualTotal'] = sum(data_dict.get(f'TotalQ{i}', 0) for i in range(1, 5))
        return json.dumps(data_dict)
    
    # Apply the function to each column
    df_json.iloc[:, 1:] = df_json.iloc[:, 1:].applymap(add_annual_total)

    return df_json.to_csv(index=False)