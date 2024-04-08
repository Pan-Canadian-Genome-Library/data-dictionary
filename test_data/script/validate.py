# This code validates input files ("study_test.tsv", "participant_test.tsv", "specimen_test.tsv" and "sample_test.tsv")
# against JSON schema ("dictionary.json"). 
# It 1) validates that "required" fields are present; and
#    2) validates data types and the match to defined lists and specific regular expressions. 
# Author: Guanqiao Feng
# Date: 2024-04-02


import pandas as pd
import json
import re

# Function to validate required columns for a given schema
def validate_required_columns(df, schema, schema_name):
    required_fields = [field['name'] for field in schema['fields'] if field['restrictions'].get('required', False)]
    cols_ok = all(col in df.columns for col in required_fields)
    print(f"All required columns present in {schema_name} schema: {cols_ok}")

# Mapping between JSON schema types and pandas types
type_mapping = {
    'string': 'object',  # In pandas, strings are typically stored as objects
    # Add more mappings as needed, e.g., 'integer': 'int64', 'number': 'float64', etc.
}

# Function to check if data matches the defined list (enumeration)
def validate_code_list(column, code_list):
    # Checking if all elements in the column exist in the code list
    invalid_values = ~column.isin(code_list)
    return column[invalid_values]

# Function to check if data matches the regular expression
def validate_regex(column, pattern):
    # Using apply to check regex match across the column, marking non-matches as True
    invalid_values = ~column.apply(lambda x: bool(re.match(pattern, x)) if pd.notnull(x) else True)
    return column[invalid_values]

# Enhanced validation function
def validate_columns(df, schema, schema_name, data):
    errors = []
    for field in schema['fields']:
        field_name = field['name']
        if field_name in df.columns:
            # Validate against codeList
            if "codeList" in field['restrictions']:
                code_list_path = field['restrictions']['codeList']
                # Extract the actual code list from the JSON schema
                code_list = data['references']['list'][code_list_path.split('/')[-1]]
                invalid_values = validate_code_list(df[field_name], code_list)
                if not invalid_values.empty:
                    errors.append(f"{field_name} has values not in codeList: {invalid_values.unique()}")
            
            # Validate against regex
            if "regex" in field['restrictions']:
                regex_path = field['restrictions']['regex']
                # Extract the actual regex pattern from the JSON schema
                pattern = data['references']['regex'][regex_path.split('/')[-1]]
                invalid_values = validate_regex(df[field_name], pattern)
                if not invalid_values.empty:
                    errors.append(f"{field_name} has values not matching regex {pattern}: {invalid_values.unique()}")
        else:
            errors.append(f"Missing field: {field_name}")

    if errors:
        for error in errors:
            print(f"Error in {schema_name} schema: {error}")
    else:
        print(f"All validations passed for {schema_name} schema.")

# read JSON data
with open("../script/dictionary.json") as json_file:
    data = json.load(json_file)

# read data for validation
study_df = pd.read_csv("study_test.tsv", sep="\t")
participant_df = pd.read_csv("participant_test.tsv", sep="\t")
specimen_df = pd.read_csv("specimen_test.tsv", sep="\t")
sample_df = pd.read_csv("sample_test.tsv", sep="\t")

# Validate each DataFrame against its schema
validate_required_columns(study_df, data['schemas']['study'], 'study')
validate_required_columns(participant_df, data['schemas']['participant'], 'participant')
validate_required_columns(specimen_df, data['schemas']['specimen'], 'specimen')
validate_required_columns(sample_df, data['schemas']['sample'], 'sample')

# Validate each DataFrame against its schema
validate_columns(study_df, data['schemas']['study'], 'study', data)
validate_columns(participant_df, data['schemas']['participant'], 'participant', data)
validate_columns(specimen_df, data['schemas']['specimen'], 'specimen', data)
validate_columns(sample_df, data['schemas']['sample'], 'sample', data)
