#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
/*
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
 */
"""

import json
import glob
import urllib
import requests
import re
import numpy as np
import os
import random
import jsonschema
import string
import time
import random
import hashlib
import shutil
import argparse
import copy
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition

def main():
  """
  The script aims to translate the FULL linkML model to lectern syntax.
  """
  parser = argparse.ArgumentParser(description='The script aims to translate the FULL linkML model to lectern syntax.')
  parser.add_argument('-c', '--custom_linkml', dest="custom_linkml", help="The custom full LinkML schema", required=True,type=str)
  parser.add_argument('-r', '--restrictions_json', dest="restrictions_json", help="The custom schema that makes references to extension and base schemas", required=False,type=str)
  parser.add_argument('-o', '--output_directory', dest="output_directory", help="Output directory to save the Lectern JSON schema", default=os.getcwd(),type=str)


  cli_input= parser.parse_args()

  if not cli_input.custom_linkml.endswith("_full.yaml"):
    print("%s does not end with the correct suffix. Please check the correct yaml was provided." % (cli_input.custom_linkml))

  model=yaml_loader.load(cli_input.custom_linkml, SchemaDefinition)

  lectern={}

  populateLecternProperties(model,lectern)

  populateSchemaProperties(model,lectern)

  populateFieldProperties(model,lectern)


  if cli_input.restrictions_json:
    with open(cli_input.restrictions_json, 'r') as file:
      restrictions = json.load(file)

    populateFieldRestrictionsProperties(restrictions,lectern)

  with open("%s/%s" % (cli_input.output_directory,cli_input.custom_linkml.split("/")[-1].replace("_full.yaml","_lectern.json")), 'w') as fp:
    json.dump(lectern, fp, indent=2)


def populateLecternProperties(model,lectern):
  for val in ["name","description","version"]:
      lectern[val]=model[val]
  lectern['schemas']=[]

def populateSchemaProperties(model,lectern):
  for class_key in model.classes.keys():
      tmp={}
      tmp['name']=class_key
      tmp['description']=model.classes[class_key]['description']
      tmp['fields']=[]
      lectern['schemas'].append(tmp)

def populateFieldProperties(model,lectern):
  linkmlToLecternDataTypes={
      "boolean":"boolean",
      "integer":"integer",
      "string":"string",
      "decimal":"number",
      "float":"number"
  }


  for schema in lectern['schemas']:
        class_key=schema['name']
        ###linkML Class == Lectern Schemas
        for slot in model.classes[class_key]['slots']:
            tmp={}
            tmp['meta']={}
            ###DisplayName for 
            tmp['meta']['displayName']=model['slots'][slot]['title']
            tmp['name']=slot
            tmp['description']=model['slots'][slot]['description']

            if model['slots'][slot]['required']:
                if not tmp.get('restrictions'):
                    tmp['restrictions']={}
                tmp['restrictions']['required']=True

            ###Handle mappings to other ontologies
            ###For lectern store under meta
            if model['slots'][slot]['exact_mappings']:
                if not tmp.get('meta'):
                    tmp['meta']={}
                if not tmp['meta'].get('mappings'):
                    tmp['meta']['mappings']={}
                    
                tmp['meta']['mappings']={}
                for mapping in model['slots'][slot]['exact_mappings']:
                    key=mapping.split(":")[0]
                    val=mapping.split(":")[-1]
                    tmp['meta']['mappings'][key]=val

            if model['slots'][slot]['comments']:
                if not tmp.get('meta'):
                    tmp['meta']={}
                tmp['meta']['required']=model['slots'][slot]['comments']

            if len(model['slots'][slot]['examples'])>0:
                if not tmp.get('meta'):
                    tmp['meta']={}
                    
                tmp['meta']['examples']=[]
                for example in model['slots'][slot]['examples']:
                    tmp['meta']['examples'].append(example['value'])
            
            ##Handle simple restrictions
            ###For more complex ones see populateFieldRestrictionsProperties
            if model['slots'][slot]['range']:
                ###Handle typing
                if model['slots'][slot]['range'] in linkmlToLecternDataTypes.keys():
                    tmp['valueType']=linkmlToLecternDataTypes[model['slots'][slot]['range']]
                ###Handle codelists
                elif "menu" in model['slots'][slot]['range'].lower():
                    tmp['valueType']='string'

                    if not tmp.get('restrictions'):
                        tmp['restrictions']={}
                    
                    tmp['restrictions']['codeList']=[]
                    for enum in model['enums'][model['slots'][slot]['range']]['permissible_values'].keys():
                        if enum is not None:
                            tmp['restrictions']['codeList'].append(enum)
            

            ###Handle min,max,regex restrictions
            if model['slots'][slot]['minimum_value'] is not None:
                if not tmp.get('restrictions'):
                    tmp['restrictions']={}
                if not tmp['restrictions'].get('range'):
                    tmp['restrictions']['range']={}

                tmp['restrictions']['range']['min']=model['slots'][slot]['minimum_value']
            if model['slots'][slot]['maximum_value'] is not None:
                if not tmp.get('restrictions'):
                    tmp['restrictions']={}
                if not tmp['restrictions'].get('range'):
                    tmp['restrictions']['range']={}

                tmp['restrictions']['range']['max']=model['slots'][slot]['maximum_value']
            if model['slots'][slot]['pattern']:
                if not tmp.get('restrictions'):
                    tmp['restrictions']={}
                tmp['restrictions']['regex']=model['slots'][slot]['pattern']

            ###Handle min,max,regex restrictions
            if model['slots'][slot]['multivalued'] is not None:
                ### Assume simple model and not dictionary https://linkml.io/linkml/schemas/inlining.html#no-inlining-reference-by-key
                if model['slots'][slot]['multivalued']:
                    ###
                    tmp['isArray']=True
                    tmp['delimiter']="|"
                    
            ###Add field to schema
            schema['fields'].append(tmp)

        ###Handle unique keys
        #print(class_key)
        if model['classes'][schema['name']]['unique_keys']:
            for unique_key in model['classes'][schema['name']]['unique_keys']['main']['unique_key_slots']:
                for field in schema['fields']:
                    if field['name']==unique_key:
                        #print(unique_key)
                        field['unique']=True
                        
  ###Handle foreign keys
  for entity in lectern['schemas']:
    for field in entity['fields']:
        if field['name'].endswith("_id") and field['name'].startswith("submitter_"):
            if field['name']=='study_id':
                continue
            if entity['name'].lower() not in field['name']:
                if not entity.get('restrictions'):
                    entity['restrictions']={}
                if not entity['restrictions'].get('foreignKey'):
                    entity['restrictions']['foreignKey']=[]

                entity['restrictions']['foreignKey'].append(
                    {
                        "schema":field['name'].replace("_id","").replace("submitter_",""),
                        "mappings": [
                            {
                                "local":field['name'],
                                "foreign":field['name']
                            }
                        ]
                    }
                )
        

  ###rename to remove capitalization:
  for schema in lectern['schemas']:
    schema['name']=schema['name'].lower()

def populateFieldRestrictionsProperties(restrictions,lectern):
  ###Interim solution
  ###linkML rules are defined in class/entity while for lectern rules are defined in slot/field
  ###linkML/Lectern
  ###precondition/if
  ###postcondition/then
  ###elsecondtion/else
  ###Example in linkML
  ###any_of/case:"any"
  ###exactly_one_of/
  ###none_of/case:"none"
  ###all_of/case:"all"
  ###equals_number/match
  ###exact_cardinality/count:{2}
  ###minimum_cardinality/count:{"min":2}
  ###maximum_cardinality/count:{"max":2}
  ###equals_string/match
  ###value_presence/exists
  ####ABSENT/False
  ####PRESENT/True
  # - preconditions:
  #     description: An example of if fieldA is missing provide fieldA_null_reason.
  #       Common in virus-seq
  #     slot_conditions:
  #       image_processing_personel:
  #         name: image_processing_personel
  #         any_of:
  #         - value_presence: ABSENT
  #   postconditions:
  #     slot_conditions:
  #       image_processing_null_reason:
  #         name: image_processing_null_reason
  #         range: ImageProcessingNullReasonMenu
  #         value_presence: PRESENT
  #       image_processing_personel:
  #         name: image_processing_personel
  #         value_presence: ABSENT
  #   elseconditions:
  #     slot_conditions:
  #       image_processing_personel:
  #         name: image_processing_personel
  #         range: string
  #       image_processing_null_reason:
  #         name: image_processing_null_reason
  #         value_presence: ABSENT
  ###Example in Lectern
  # {
  #   "name": "image_processing_personel",
  #   "restrictions": {
  #     "if": {
  #       "conditions": [
  #         {
  #           "field": "Image Processing Null Reason",
  #           "exists": false
  #         }
  #       ],
  #       "case": "all"
  #     },
  #     "then": {
  #       "required": true,
  #       "valueType": "string"
  #     }
  #   }
  # },
  # {
  #   "name": "image_processing_null_reason",
  #   "restrictions": {
  #     "if": {
  #       "conditions": [
  #         {
  #           "field": "Image Processing Personel",
  #           "exists": false
  #         }
  #       ],
  #       "case": "all"
  #     },
  #     "then": {
  #       "required": true,
  #       "codeList": [
  #         "Unknown",
  #         "Not Provided",
  #         "Revoked"
  #       ]
  #     },
  #     "else": {
  #       "empty": true
  #     }
  #   }
  ### if statements in both remain the ssame
  ### in linkML post and else conditions can affect multiple fields b/c the rule is set in the class/schema
  ### in lectern only one field is affected at a time b/c the rule is set in the field
  ### linkML also handles case statement more elegantly b/c it allows for multiple if statements
  ### For lectern, the if statements have to be chained together under else
  for restrict_schema in restrictions['schemas']:
      for lectern_schema in lectern['schemas']:
          ###Find corresponding entity in restrictions.json and lectern
          #print(lectern_schema['name'],restrict_schema['name'],"schema")
          if restrict_schema['name'].lower()==lectern_schema['name'].lower():
              for restrict_field in restrict_schema['fields']:
                  for lectern_field in lectern_schema['fields']:
                      #print(lectern_field['name'],restrict_field['name'],"field")
                      ###Find corresponding field in restrictions.json and lectern
                      if lectern_field['name'].lower()==restrict_field['name'].lower():
                          lectern_field['restrictions']=restrict_field['restrictions']


if __name__ == "__main__":
    main()