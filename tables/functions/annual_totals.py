from django.core.files.base import ContentFile
import pandas as pd
import os
import ast
import json

def group_files_by_year(sums_directory):
    year_groups = {}  # Dictionary to store files grouped by year
    for file in os.listdir(sums_directory):
        if file.startswith('sums'):
            year = int(file.split('_')[-1][:4])  # Extract the year from the file name
            if year == 2020:
                if 'juldec' in file:
                    year_group = f"{year}{year+1}"
                else:
                    continue  # Skip files for Jan-Jun 2020
            else:
                if 'julsep' in file:
                    year_group = f"{year}{year+1}"
                elif 'octdec' in file:
                    year_group = f"{year}{year+1}"
                elif 'janmar' in file:
                    year_group = f"{year-1}{year}"
                elif 'aprjun' in file:
                    year_group = f"{year-1}{year}"
                else:
                    raise TypeError("Invalid quota")
            if year_group not in year_groups:
                year_groups[year_group] = []
            year_groups[year_group].append(file)
    return year_groups


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


def compute_annual_totals(sums_directory, Grantee):
    
    year_groups = group_files_by_year(sums_directory)
    dfs_by_group = {}

    for year_group, csv_files in year_groups.items():
        dfs = []
        for csv_file in csv_files:
            df = pd.read_csv(os.path.join(sums_directory, csv_file))
            code_columns = df.columns[1:]
            for column in code_columns:
                df[column] = df[column].apply(convert_to_dict)
            dfs.append(df)

        combined_df = pd.concat(dfs)
        sum_df = combined_df.groupby("district").agg(lambda x: sum_dictionaries(x)).reset_index()
        dfs_by_group[year_group] = sum_df

    for year_group, df in dfs_by_group.items():
        df0 = df.drop('district', axis=1).applymap(json.dumps)
        df = pd.concat([df['district'], df0], axis=1)

        return year_group, ContentFile(df.to_csv(index=False))
        

