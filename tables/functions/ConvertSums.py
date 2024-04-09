import pandas as pd
import ast
import json
import warnings
import os
from django.core.files.base import ContentFile

"""
    Create a function for custom rounding
"""
def custom_round(x):
    try:
        return round(float(x))
    except ValueError:
        return x
    

"""
    Convert the excel file and obtain sheets then convert to the required format.
    Take inputs as grantee and file and obtain the individual sheets for processing
"""
def CreateSUMS(grantee, file):
    csvs_list={}
    # Suppress openpyxl warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

    # Output folder
    output_folder = "../output"

    # Read all sheets into a dictionary of dataframes
    xls = pd.ExcelFile(file)
    # Read all sheets into a dictionary of dataframes
    all_sheets = pd.read_excel(file, sheet_name=None)

    # Define sheets to exclude from further processing (if any)
    exclude_sheets = ["Read Me"]

    # Filter out excluded sheets
    sheets_to_process = {sheet_name: all_sheets[sheet_name] for sheet_name in all_sheets if sheet_name not in exclude_sheets}

        # Iterate through each sheet in the Excel file
    # Step 2: Apply the algorithm to each sheet and save individual CSVs
    
    # Iterate through each sheet in the Excel file
    for sheet_name, df in sheets_to_process.items():
        # Initial data cleanup
            # Custom rounding function
        def custom_round(x):
            try:
                return round(float(x))
            except ValueError:
                return x
                
        #!!!!!!!!! Convert datetime objects to strings
        df = df.astype(str)
        # !!!!!!
        
        # Applying custom rounding function to columns A and B
        for col in df.columns:
            df[col] = df[col].apply(custom_round)
    
       
        df= df.drop('Code', axis = 1)
        df = df.drop(0)
    
        # Initialize the header variable
        current_header = None
    
        # Create a dictionary to store the mapping of headers
        header_mapping = {}
    
        for col in df.columns:
            col_name = str(col)  # Convert the column name to a string
    
            if col_name.startswith("Unnamed:"):
                if current_header is not None:
                    header_mapping[col_name] = current_header
            else:
                current_header = col_name
    
        df.rename(columns=header_mapping, inplace=True)
    
        # Now, the DataFrame will have columns with headers like '1.1', '1.1', '1.1', '3.11', '3.11', '3.11', '3.11'
    
    
        # Define the new column names
        new_column_names = {
            'Unnamed: 0': 'Region',
            'Unnamed: 1': 'District'
        }
    
        # Rename the specified columns
        df = df.rename(columns=new_column_names)
    
    
        # Extract the values from row 1
        suffixes = df.iloc[0].tolist()
    
    
        # Replace spaces with underscores in each feature
        modified_list = [feature.replace(' ', '_') for feature in suffixes]
    
        # Rename the columns with the values from row 1 as suffixes
        df.columns = [f'{col}_{suffix}' for col, suffix in zip(df.columns, modified_list)]
    
        df = df.drop(1)
    
        # Define the new column names
        new_column_names = {
            'Region_Region': 'Region',
            'District_District': 'District'
        }
    
        # Rename the specified columns
        df = df.rename(columns=new_column_names)
    
        df = df.reset_index(drop=True)
    
        # Replace "Jul - Sep 2021" with 0 in a specific column if the value exists
        column_name = '3.4_Youth_Male'
        # Replace with the actual column name
        if column_name in df.columns:
            if 'Jul - Sep 2021' in df[column_name].values:
                df[column_name] = df[column_name].replace('Jul - Sep 2021', 0)
    
        # List of columns to exclude from conversion to int
        exclude_columns = ["Region", "District"]
    
        # Iterate through columns and convert to int if not in the exclusion list
        for column in df.columns:
            if column not in exclude_columns:
                df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer')
    
        df.fillna(0, inplace=True)
    
        # Initialize an empty dictionary to store the transformed data
        data = {}
    
        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            district = row['District']
            data[district] = row.drop('District').to_dict()
    
        # List of columns to exclude from conversion to int
        exclude_columns = ["Region", "District"]
    
        # Iterate through columns and convert to int if not in the exclusion list
        for column in df.columns:
            if column not in exclude_columns:
                df[column] = pd.to_numeric(df[column], errors='coerce', downcast='integer')
    
        # Compute column sums
        column_totals = df.select_dtypes(include='number').sum()
        
        # Check and adjust totals using 'All (National Coverage)'
        for col in column_totals.index:
            if df.loc[df['Region'] == 'All (National Coverage)', col].values[0] > 0:
                column_totals[col] = df.loc[df['Region'] == 'All (National Coverage)', col].values[0]
        
        # Create a new row with the totals
        total_row = pd.DataFrame(column_totals).T
        total_row['Region'] = 'Total'
        total_row['District'] = 'Total'
        
        # Concatenate the total row to the DataFrame
        df = pd.concat([df, total_row], ignore_index=True)
    
    
        # Assuming df is your DataFrame
        # Create a nested dictionary
        district_dict = {}
        for index, row in df.iterrows():
            district_name = row["District"]
            district_dict[district_name] = {}
    
            for column in df.columns:
                if column != "District" and "_" in column:
                    main_key, sub_key = column.split("_", 1)
                    if main_key not in district_dict[district_name]:
                        district_dict[district_name][main_key] = {}
                    district_dict[district_name][main_key][column] = int(row[column])
    
    
       
        # Convert to JSON
        district_dict_json = json.dumps(district_dict, indent=2)
    
    
        # Create a DataFrame
        df_list = []
        for district, values in district_dict.items():
            row = {"District": district}
            row.update(values)
            df_list.append(row)
    
        df = pd.DataFrame(df_list)
    
        # Convert all columns except 'District' to JSON in each cell
        df_json = df.drop('District', axis=1).applymap(json.dumps)
    
        # Add the 'District' column back to the DataFrame at the beginning
        df_json = pd.concat([df['District'], df_json], axis=1)
    
        df_json.columns = df_json.columns.str.replace('.', '_')
    
        # Assuming df is your DataFrame
        df_json.columns = ['code' + col.replace('_', '') if col != 'District' else col for col in df_json.columns]
    
        import ast
        df = df_json
    
        # Convert string representations of dictionaries to actual dictionaries
        for column in df.columns[1:]:
            df[column] = df[column].apply(ast.literal_eval)
    
        # Remove prefixes from keys in nested dictionaries
        for column in df.columns[1:]:
            df[column] = df[column].apply(lambda x: {key.split('_', 1)[1]: value for key, value in x.items()})
    
    
        # Convert all columns except 'District' to JSON in each cell
        df_json = df.drop('District', axis=1).applymap(json.dumps)
    
        # Add the 'District' column back to the DataFrame at the beginning
        df_json = pd.concat([df['District'], df_json], axis=1)
        df_json = df_json.rename(columns=lambda x: x.replace(' ', ''))
    
        # Specify the current column names and the new column names
        column_mapping = {
            'old_column_name1': 'code 1515',
            'old_column_name2': 'code1515',
            # Add more entries as needed
        }
    
        # Use the rename method to rename the columns
        df_json = df_json.rename(columns=column_mapping)
    
        # Define the new column names
        new_column_names = {
            'District': 'district'
    
        }
    
        # Rename the specified columns
        df_json = df_json.rename(columns=new_column_names)
        # Drop rows where 'district' column is nan
        df_json = df_json[df_json['district'] != 'nan']
        df_json = df_json[df_json['district'] != 0]
        df_json=df_json.dropna(how='all')
        #change the sheet names
        new_sheet_name=sheet_name.replace('-','')
        new_sheet_name=new_sheet_name.replace('  ','')
        new_sheet_name=new_sheet_name.replace('April','Apr')
        new_sheet_name=new_sheet_name.replace('June','Jun')
        sheet_name_list=new_sheet_name.split(" ")
        new_sheet_name=sheet_name_list[0].casefold()+"_"+sheet_name_list[1]
        df_json.to_csv('test_file.csv',index=False)
        filename=f'sums_{grantee}_{new_sheet_name}'.casefold()
        
        # # Final CSV Export:
        # # output_csv_path = os.path.join(output_folder, f"SUMS_{grantee}_{sheet_name}.csv")
        # df_json.to_csv(index=False)
        csvs_list[filename]=ContentFile(df_json.to_csv(index=False))
    return csvs_list