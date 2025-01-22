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

  templates={}
  for lm_class in model.classes:
    templates[lm_class]=pd.DataFrame()
    populateDataFrame(model,templates[lm_class],lm_class)

  for key in templates.keys():
    templates[key].to_csv("%s/%s_template.tsv" % (cli_input.output_directory,key.lower()),sep='\t')


  #templates=initialize_dataframe()

  #populateDataFrame(model,definitions)

  #definitions.to_csv("%s/%s" % (cli_input.output_directory,cli_input.custom_linkml.split('/')[-1].replace("_full.yaml","_flattened.tsv")),index=True,sep='\t')


def populateDataFrame(model,template,key):
  for slot in model.classes[key]['slots']:
      template[slot]=None

if __name__ == "__main__":
    main()