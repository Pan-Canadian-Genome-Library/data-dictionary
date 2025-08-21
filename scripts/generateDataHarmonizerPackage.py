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
import subprocess
import pandas as pd
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition

def main():
  """
  The script aims to repackage the data harmonizer, replacing the contents with PCGL schemas 
  """
  parser = argparse.ArgumentParser(description='The script aims to repackage the data harmonizer, replacing the contents with PCGL schemas.')
  parser.add_argument('-d', '--data_harmonizer_url', dest="data_harmonizer_url", help="The custom full LinkML schema",type=str,default="https://github.com/cidgoh/DataHarmonizer/archive/refs/tags/v1.6.5.tar.gz")
  parser.add_argument('-o', '--output_directory', dest="output_directory", help="Output directory to save the Data Harmonizer tar", default=os.getcwd(),type=str)
  parser.add_argument('-s', '--schema_directory', dest="schema_directory", help="Schema directory containing PCGL schemas",type=str,required=True)


  cli_input= parser.parse_args()

  ###Set working directory
  os.chdir(cli_input.output_directory)

  ###Download base DH package
  cmd=["curl","-OL", cli_input.data_harmonizer_url]
  try:
     subprocess.run(cmd)
  except subprocess.CalledProcessError:
     print("the following command failed:")
     print("".join(cmd))
     exit(1)

  ###Untar base dh package
  cmd=["tar","-xvzf", cli_input.data_harmonizer_url.split("/")[-1]]
  try:
      subprocess.run(cmd)
  except subprocess.CalledProcessError:
      print("the following command failed:")
      print("".join(cmd))
      exit(1)

  ###Check if expected output dir exists
  tar_dir="%s/%s-%s" % (cli_input.output_directory,"DataHarmonizer",re.search('[0-9]\\.[0-9]\\.[0-9]', cli_input.data_harmonizer_url.split("/")[-1])[0])
  if not os.path.exists(tar_dir):
      print("ERROR data harmonizer directory does not exist")
      print(tar_dir)
      exit(1)

  ###Clean up example directories - Leaving one to fulfill dependencies:
  for z in ["ambr","canada_covid19","gisaid","grdi","influenza","pathogen","pha4ge","phac_dexa","wastewater"]:
      cmd=["rm","-r","%s/web/templates/%s" % (tar_dir,z)]
      try:
          subprocess.run(cmd)
      except subprocess.CalledProcessError:
          print("the following command failed:")
          print("".join(cmd))
          exit(1)

  ###Empty examples in JSON
  menu_json="%s/web/templates/%s" % (tar_dir,"menu.json")

  cmd=["cd",tar_dir]
  try:
      subprocess.run(cmd)
  except subprocess.CalledProcessError:
      print("the following command failed:")
      print("".join(cmd))
      exit(1)
          
  with open(menu_json, 'w') as f:
      json.dump({}, f)

  ###Run per dh.yaml detected in schema_directory
  for yaml in glob.iglob("%s/*/*_dh.yaml" % (cli_input.schema_directory)):
      data_dir=yaml.split("/")[-1].replace("_dh.yaml","")

      ###Make new project directory in dataHarmonizer directory
      cmd=["mkdir","-p","%s/web/templates/%s" % (tar_dir,data_dir)]
      try:
          subprocess.run(cmd)
      except subprocess.CalledProcessError:
          print("the following command failed:")
          print("".join(cmd))
          exit(1)

      ###copy over dh yaml
      cmd=["cp",yaml,"%s/web/templates/%s/schema.yaml" % (tar_dir,data_dir)]
      try:
          subprocess.run(cmd)
      except subprocess.CalledProcessError:
          print("the following command failed:")
          print("".join(cmd))
          exit(1)

      ###The next follow step writes to current working directory, we need that to be the project specifc directory
      os.chdir("%s/web/templates/%s" % (tar_dir,data_dir))

      
      ###Run data harmonizer linkml script to convert yaml to json
      cmd=["python","%s/script/linkml.py" % (tar_dir),"-i","%s/web/templates/%s/schema.yaml"  % (tar_dir,data_dir)]
      try:
          subprocess.run(cmd)
      except subprocess.CalledProcessError:
          print("the following command failed:")
          print("".join(cmd))
          exit(1)

      ###Copy over export typescript from PCGL schema directory
      cmd=["cp","%s/%s" % (os.path.dirname(yaml.replace("custom","typescript_export")),"export.js"),"%s/web/templates/%s/export.js"  % (tar_dir,data_dir)]
      try:
          subprocess.run(cmd)
      except subprocess.CalledProcessError:
          print("the following command failed:")
          print("".join(cmd))
          exit(1)

  ###Return back to original working directory
  os.chdir(cli_input.output_directory)

  ###Compress data directory
  cmd=["tar","czf", "data_harmonizer.tar.gz",tar_dir.split("/")[-1]]
  try:
      subprocess.run(cmd)
  except subprocess.CalledProcessError:
      print("the following command failed:")
      print("".join(cmd))
      exit(1)

  ###Clean up
  cmd=["rm","-r",tar_dir]
  try:
      subprocess.run(cmd)
  except subprocess.CalledProcessError:
      print("the following command failed:")
      print("".join(cmd))
      exit(1)

if __name__ == "__main__":
  main()