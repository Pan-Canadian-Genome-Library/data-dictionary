#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
  Copyright (C) 2022,  icgc-argo

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU Affero General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Affero General Public License for more details.

  You should have received a copy of the GNU Affero General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  Authors:
    Edmund Su
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
import pandas as pd
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition

def main():
  """
  The script aims to translate the FULL linkML model to lectern syntax.
  """
  parser = argparse.ArgumentParser(description='The script aims to translate the FULL linkML model to flatten TSV for viewing.')
  parser.add_argument('-c', '--custom_linkml', dest="custom_linkml", help="The custom full LinkML schema", required=True,type=str)
  parser.add_argument('-o', '--output_directory', dest="output_directory", help="Output directory to save the Lectern JSON schema", default=os.getcwd(),type=str)


  cli_input= parser.parse_args()

  if not cli_input.custom_linkml.endswith("_full.yaml"):
    print("%s does not end with the correct suffix. Please check the correct yaml was provided." % (cli_input.custom_linkml))

  model=yaml_loader.load(cli_input.custom_linkml, SchemaDefinition)

  definitions=initialize_dataframe()

  populateDataFrame(model,definitions)

  definitions['schema']=[val.lower() for val in definitions['schema'].values.tolist()]
  definitions.to_csv("%s/%s" % (cli_input.output_directory,cli_input.custom_linkml.split('/')[-1].replace("_full.yaml","_flattened.tsv")),index=False,sep='\t')

def initialize_dataframe():
  df=pd.DataFrame()
  df['field']=None
  df['schema']=None
  df['required']=None
  df['dataType']=None
  df['description']=None
  df['comments']=None
  df['exact_mappings']=None
  return df

def populateDataFrame(model,definitions):
  count=0
  for lm_class in model.classes:
      for slot in model.classes[lm_class]['slots']:
          definitions.loc[count,"field"]=slot
          definitions.loc[count,"schema"]=lm_class
          count+=1

  for ind in definitions.index.values.tolist():
      slot=definitions.loc[ind,"field"]
      key="required"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          definitions.loc[ind,key]=model.slots[slot][key]
      else:
          definitions.loc[ind,key]=False
          
      key="range"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          if "Menu" in model.slots[slot][key]:
              definitions.loc[ind,"dataType"]="string"
          else:
              definitions.loc[ind,"dataType"]=model.slots[slot][key]
      else:
          definitions.loc[ind,"dataType"]=False

      key="description"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          definitions.loc[ind,key]=model.slots[slot][key]
      else:
          definitions.loc[ind,key]=None

      key="comments"
      if key in model.slots[slot] and len(model.slots[slot][key])!=0:
          definitions.loc[ind,key]=model.slots[slot][key]
      else:
          definitions.loc[ind,key]=None

      key="exact_mappings"
      if key in model.slots[slot] and len(model.slots[slot][key])!=0:
          definitions.loc[ind,key]=";".join(model.slots[slot][key])
      else:
          definitions.loc[ind,key]=None

      validation_rules=[]

      key="pattern"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          #print(key,ind)
          validation_rules.append("%s:%s" % (key,model.slots[slot][key]))
          #print(validation_rules)
          
      key="minimum_value"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          #print(key,ind)
          validation_rules.append("%s:%s" % (key,str(model.slots[slot][key])))
          #print(validation_rules)
          
      key="maximum_value"
      if key in model.slots[slot] and model.slots[slot][key]!=None:
          #print(key,ind)
          validation_rules.append("%s:%s" % (key,str(model.slots[slot][key])))
          #print(validation_rules)

      key="range"
      if "Menu" in model.slots[slot][key]:
          #print(key,ind)
          enum_list=[]
          #validation_rules.append("%s:" % ("Enum"))
          for enum_value in model.enums[model.slots[slot][key]]['permissible_values']:
              enum_list.append(enum_value)
          validation_rules.append("%s:%s" % ("Enum",",".join(enum_list)))
          #print(validation_rules)

      if len(validation_rules)>0:
          definitions.loc[ind,"validation"]=";".join(validation_rules)

if __name__ == "__main__":
    main()