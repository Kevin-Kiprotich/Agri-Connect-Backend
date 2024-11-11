from supabase import create_client
import os
import pandas as pd
import os
import json





def create_table(file_path, supabase):
    # Load DataFrame from CSV File
    df = pd.read_csv(file_path)
    column_names = df.columns.tolist()

    # Extract District Column and JSONB Columns
    district_column_name = None
    jsonb_columns = []

    for col in column_names:
        if col.lower() == 'district':
            district_column_name = col
        else:
            jsonb_columns.append(col)

    # Extract Table Name from File Path
    file_name =   os.path.splitext(os.path.basename(file_path))[0]
    table_name = file_name.lower()


    # Call Supabase SQL Function to Create the Table
    try:
        response = supabase.rpc(
            "create_sums_table_with_dynamic_columns",
            {
                "table_name": table_name,
                "primary_key_column_name": district_column_name,
                "jsonb_columns": jsonb_columns
            }
        ).execute()
    except Exception as e:
        print(f"An error occurred: {e}")



def upsert_data(file_path, supabase):
    try:
        # Load DataFrame from CSV file
        df = pd.read_csv(file_path)
        
        # Extract table name from file path
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        table_name = file_name.lower()

        # Iterate over each row in the DataFrame
        for index, row in df.iterrows():
            # Extract the district
            district_value = row['district']
            
            # Create the dictionary with the district
            upsert_data = {
                'district': district_value,
            }
            
            # Iterate over JSONB columns
            for col in df.columns:
                if col != 'district':
                    # Parse JSONB data
                    json_data = json.loads(row[col])
                    
                    # Add JSONB data to the dictionary
                    upsert_data[col] = json_data
            
            # Upsert the data into the Supabase table
            try:
                response = supabase.table(table_name).upsert(
                    upsert_data,
                    on_conflict=['district'],  # Specify the column(s) to check for conflicts
                ).execute()
                # Uncomment the following line to print the response
                # print(f"Upserted row {index} with response: {response}")
            except Exception as e:
                print(f"An error occurred while upserting row {index} in table {table_name}: {e}")

    except Exception as e:
        print(f"An error occurred while processing file {file_path}: {e.args[0]}")



# folder_path = '../PythonScripts/genderAgg_outputs/all/SUMS'
# file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]

# # Create Table
# for file_path in file_paths:
#     create_table(file_path, supabase)

# # Insert Data
# for file_path in file_paths:
#     upsert_data(file_path, supabase)



