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
    command = ["linkml", "generate", "json-schema", input_file, "--top-class", top_class]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return result.stdout

def resolve_references(json_schema_str):
    # Resolve references in the JSON schema
    return jsonref.loads(json_schema_str)

def customize_schema(json_schema, top_class, options):
    # Customization logic here
    # Drop specific fields from the JSON schema
    # fields_to_drop = []
    fields_to_drop = ["$defs", "$id", "$schema", "additionalProperties", "metamodel_version", "description", "version", "title"]  
    for field in fields_to_drop:
        if field in json_schema:
            del json_schema[field]
    
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


def process_schema(input_file, top_class, options, output_file):
    # Generate JSON schema using linkml generate command with --top-class option
    json_schema_str = generate_json_schema(input_file, top_class)

    # Resolve references in the JSON schema
    schema_with_refs = resolve_references(json_schema_str)

    # Create a copy of the resolved schema
    schema_copy = copy.deepcopy(schema_with_refs)

    # Customize the JSON schema
    customized_schema = customize_schema(schema_copy, top_class, options)
    
    # Validate the customized schema
    validate_schema(customized_schema)

    # Write the fully expanded and customized schema to the output file.
    with open(output_file, "w", encoding="utf-8") as out:
        json.dump(customized_schema, out, indent=2)

    print(f"Expanded schema saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate and customize JSON schema from LinkML YAML file.")
    parser.add_argument("--input_file", help="The input YAML file defining the LinkML data model.", default="../song_schema/linkml/pcgl_song_dynamic.yaml")
    parser.add_argument("--config_file", help="The configuration file with key-value pairs for top_class options.", default="../song_schema/conf/options.json")
    parser.add_argument("--output_dir", help="The directory to save the expanded schemas.", default="../song_schema/json-schema")

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
        output_file = os.path.join(args.output_dir, f"{top_class}.json")
        process_schema(args.input_file, top_class, options, output_file)

if __name__ == "__main__":
    main()