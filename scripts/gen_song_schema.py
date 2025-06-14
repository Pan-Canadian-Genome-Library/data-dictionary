#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
 * Copyright (c) 2025 The Ontario Institute for Cancer Research. All rights reserved
 *
 * This program and the accompanying materials are made available under the terms of
 * the GNU Affero General Public License v3.0. You should have received a copy of the
 * GNU Affero General Public License along with this program.
 *  If not, see <http://www.gnu.org/licenses/>.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
 * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
 * OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
 * SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
 * INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
 * TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 * OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
 * IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
 * ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import sys
import os
import json
import jsonref
import subprocess
import copy
import argparse
from jsonschema import exceptions

# We'll import all relevant validators that jsonschema provides
from jsonschema.validators import (
    Draft7Validator,
    Draft201909Validator,
    Draft202012Validator
)


def generate_json_schema(input_file, top_class):
    # Use the linkml generate command to generate JSON schema with --top-class option and capture output
    command = ["linkml", "generate", "json-schema", "--top-class", top_class, input_file] 
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("Command executed successfully.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error occurred while running the command.")
        print("Command:", e.cmd)
        print("Return Code:", e.returncode)
        print("Standard Output:", e.stdout)
        print("Standard Error:", e.stderr)
        raise  

def resolve_references(json_schema_str):
    # Resolve references in the JSON schema
    return jsonref.loads(json_schema_str)

def drop_fields(json_schema, fields_to_drop):
    for field in fields_to_drop:
        if field in json_schema:
            del json_schema[field]
    return json_schema

def remove_titles(schema):
    # Recursively remove all "title" fields from the schema
    if isinstance(schema, dict):
        schema.pop("title", None)
        for key, value in schema.items():
            remove_titles(value)
    elif isinstance(schema, list):
        for item in schema:
            remove_titles(item)

def generate_dynamic_schema(json_schema, top_class, options):
    # Drop specific fields from the JSON schema
    # fields_to_drop = []
    fields_to_drop = ["$id", "$schema", "additionalProperties", 
                      "metamodel_version", "description", 
                      "version", "title"]  
    json_schema = drop_fields(json_schema, fields_to_drop)
    property_fields_to_drop = ["files", "analysisType", "studyId"]
    json_schema['properties'] = drop_fields(json_schema['properties'], property_fields_to_drop)

    # Remove specific values from the required list
    json_schema['required'] = [field for field in json_schema['required'] if field not in property_fields_to_drop]

    # Reorganize the schema
    reorganized_schema = {
        "name": top_class,
        "options": options,
        "schema": json_schema
    }
    return reorganized_schema

def validate_schema(schema):
    # Validate the schema with different drafts
    validators = [Draft7Validator, Draft201909Validator, Draft202012Validator]
    for validator in validators:
        try:
            validator.check_schema(schema)
            print(f"Schema is valid with {validator.META_SCHEMA['$id']}")
        except exceptions.SchemaError as e:
            print(f"Schema is not valid with {validator.META_SCHEMA['$id']}: {e}")


def generate_template(schema):
    # Generate a template instance based on the schema
    template = {}
    for prop, prop_schema in schema.get('properties', {}).items():
        if 'const' in prop_schema:
            template[prop] = prop_schema['const']
        elif 'enum' in prop_schema:
            template[prop] = f"<{prop}>"
        elif 'pattern' in prop_schema:
            template[prop] = f"<{prop}>"
        elif 'type' in prop_schema:
            prop_type = prop_schema['type']
            if isinstance(prop_type, list):
                if 'null' in prop_type:
                    prop_type.remove('null')
                    if not prop_type:
                        template[prop] = None
                        continue
                    prop_type = prop_type[0]
            if prop_type == 'string':
                template[prop] = f"<{prop}>"
            elif prop_type == 'integer':
                template[prop] = 0
            elif prop_type == 'number':
                template[prop] = 0.0
            elif prop_type == 'boolean':
                template[prop] = False
            elif prop_type == 'array':
                if 'items' in prop_schema and 'enum' in prop_schema['items']:
                    template[prop] = [f"<{prop}>"]
                else:
                    template[prop] = [generate_template(prop_schema['items'])]
            elif prop_type == 'object':
                template[prop] = generate_template(prop_schema)
    return template


def update_schema(schema, top_class, file_type_enum, data_type_enum):
    # Update the name property within the analysisType property to be a constant value from top_class
    if 'analysisType' in schema.get('properties', {}):
        if 'properties' in schema['properties']['analysisType']:
            schema['properties']['analysisType']['properties']['name'] = {"const": top_class}
    
    # Update the fileType and dataType properties to be enum lists from file_type_enum and data_type_enum
    if 'files' in schema.get('properties', {}):
        if 'items' in schema['properties']['files']:
            if 'properties' in schema['properties']['files']['items']:
                if 'fileType' in schema['properties']['files']['items']['properties']:
                    schema['properties']['files']['items']['properties']['fileType']['enum'] = file_type_enum
                if 'dataType' in schema['properties']['files']['items']['properties']:
                    schema['properties']['files']['items']['properties']['dataType']['enum'] = data_type_enum
    return schema

def ensure_directory_exists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def process_schema(input_file, top_class, options, schema_dir):
    
    # Generate JSON schema using linkml generate command with --top-class option
    json_schema_str = generate_json_schema(input_file, top_class)

    # Resolve references in the JSON schema
    schema_with_refs = resolve_references(json_schema_str)

    # # Create a copy of the resolved schema
    # schema_copy = copy.deepcopy(schema_with_refs)

    # Drop specific fields and update the JSON schema
    fields_to_drop = ["$id", "$defs", "description", "version", "title",
                      "additionalProperties", "metamodel_version"]
    schema_clean = drop_fields(copy.deepcopy(schema_with_refs), fields_to_drop)

    # Update the name property within the analysisType property
    file_type_enum = options.get('options', []).get('fileTypes', [])
    data_type_enum = options.get('dataType', []) 
    schema_clean = update_schema(schema_clean, top_class, file_type_enum, data_type_enum)

    # Remove all "title" fields from the schema
    remove_titles(schema_clean)

    # Prepare output paths
    full_schema_path = os.path.join(schema_dir, "full", f"{top_class}.json")
    template_path = os.path.join(schema_dir, "template", f"{top_class}_template.json")
    dynamic_schema_path = os.path.join(schema_dir, "dynamic", f"{top_class}.json")

    # Ensure all output directories exist
    for path in [full_schema_path, template_path, dynamic_schema_path]:
        ensure_directory_exists(os.path.dirname(path))

    # Write full schema
    with open(full_schema_path, "w", encoding="utf-8") as out:
        json.dump(schema_clean, out, indent=2)
    print(f"Expanded full schema saved to: {full_schema_path}")

    # Generate and write template
    template_instance = generate_template(copy.deepcopy(schema_clean))
    with open(template_path, "w", encoding="utf-8") as out:
        json.dump(template_instance, out, indent=2)
    print(f"Template instance saved to: {template_path}")

    # Generate, validate, and write dynamic schema
    dynamic_schema = generate_dynamic_schema(copy.deepcopy(schema_clean), top_class, options.get('options', {}))
    validate_schema(dynamic_schema)
    with open(dynamic_schema_path, "w", encoding="utf-8") as out:
        json.dump(dynamic_schema, out, indent=2)
    print(f"Expanded dynamic schema saved to: {dynamic_schema_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate and customize JSON schema from LinkML YAML file.")
    parser.add_argument("--input_file", help="The input YAML file defining the LinkML data model.", default="../song_schema/linkml/pcgl_song_schema.yaml")
    parser.add_argument("--config_file", help="The configuration file with key-value pairs for top_class options.", default="../song_schema/conf/options.json")
    parser.add_argument("--output_schema_dir", help="The directory to save the expanded schemas.", default="../song_schema/json-schema")
    
    args = parser.parse_args()

    # Load the configuration file
    if os.path.exists(args.config_file):
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        print(f"Configuration file {args.config_file} not found.")
        sys.exit(1)

    # Loop through each key in the configuration file and generate JSON schema for each top_class
    for top_class, options in config.items():
        # output_file = os.path.join(args.output_dir, f"{top_class}")
        process_schema(args.input_file, top_class, options, args.output_schema_dir)

if __name__ == "__main__":
    main()