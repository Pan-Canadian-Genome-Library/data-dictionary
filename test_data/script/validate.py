# This code validates input files ("study_test.tsv", "participant_test.tsv", "specimen_test.tsv" and "sample_test.tsv")
# against JSON schema ("dictionary.json"). 
# It 1) validates that "required" fields are present; and
#    2) validates data types and the match to defined lists and specific regular expressions. 
# Author: Guanqiao Feng
# Date: 2024-04-02

import pandas as pd
import json
import re
import sys
import glob
import os

# Function to validate required columns for a given schema
def validate_required_columns(df, schema, schema_name):
    required_fields = [field['name'] for field in schema['fields'] if field['restrictions'].get('required', False)]
    cols_ok = all(col in df.columns for col in required_fields)
    print(f"{schema_name}: All required columns present -> {cols_ok}")

# Mapping between JSON schema types and pandas types
type_mapping = {
    'string': 'object',  # In pandas, strings are typically stored as objects
    # Add more mappings as needed, e.g., 'integer': 'int64', 'number': 'float64', etc.
}

# Function to check if data matches the defined list (enumeration)
def validate_code_list(column, code_list):
    invalid_rows = []
    for index, value in column.items():
        if value not in code_list:
            invalid_rows.append((index, value))
    return invalid_rows

# Function to check if data matches the regular expression
def validate_regex(column, pattern):
    invalid_rows = []
    for index, value in column.items():
        if pd.notnull(value) and not re.match(pattern, value):
            invalid_rows.append((index, value))
    return invalid_rows

def validate_columns(df, schema, schema_name, data):
    errors = []
    for field in schema['fields']:
        field_name = field['name']
        if field_name in df.columns:
            # Validate against codeList
            if "codeList" in field['restrictions']:
                code_list_path = field['restrictions']['codeList']
                code_list = data['references']['list'][code_list_path.split('/')[-1]]
                invalid_rows = validate_code_list(df[field_name], code_list)
                if invalid_rows:
                    errors.extend([f"{schema_name}: Error -> row {row+2} {field_name} has values not in codeList: {value}" for row, value in invalid_rows])
            
            # Validate against regex
            if "regex" in field['restrictions']:
                regex_path = field['restrictions']['regex']
                pattern = data['references']['regex'][regex_path.split('/')[-1]]
                invalid_rows = validate_regex(df[field_name], pattern)
                if invalid_rows:
                    errors.extend([f"{schema_name}: Error -> row {row+2} {field_name} has values not matching regex {pattern}: {value}" for row, value in invalid_rows])
        else:
            errors.append(f"{schema_name}: Missing field: {field_name}")

    if errors:
        for error in errors:
            print(error)
    else:
        print(f"{schema_name}: All validations passed -> True")


# read JSON data
with open("../script/dictionary.json") as json_file:
    data = json.load(json_file)

# # Function to read and validate a single file
def validate_file(filepath, data):
    filename = os.path.basename(filepath)  # Extract the filename from the full path
    schema_name = filename.split("_")[0]  # Use the filename to extract the schema name
    if schema_name in data['schemas']:
        df = pd.read_csv(filepath, sep="\t")  # Use the full filepath to read the file
        validate_required_columns(df, data['schemas'][schema_name], schema_name)
        validate_columns(df, data['schemas'][schema_name], schema_name, data)
    else:
        print(f"No schema found for {schema_name}, skipping {filename}")
    print()

# Main function to handle command-line arguments
def main():
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        if os.path.isdir(first_arg):  # If the argument is a directory
            path = os.path.join(first_arg, '*.tsv')  # Search for all TSV files
            files_to_validate = glob.glob(path)
        else:
            files_to_validate = sys.argv[1:]  # Treat as individual file names
    else:
        # Default file list if no arguments are provided
        default_files = ["study_test.tsv", "participant_test.tsv", "specimen_test.tsv", "sample_test.tsv"]
        files_to_validate = default_files

    for filename in files_to_validate:
        validate_file(filename, data)

if __name__ == "__main__":
    main()
