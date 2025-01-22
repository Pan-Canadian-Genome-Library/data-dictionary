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
from linkml_runtime.loaders import yaml_loader
from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition

def main():
    """
	The script aims to repackage and flatten the inherited classes in extension and base producing a Data Harmonizer friendly and non-reference versions of the custom schema.
    """
    parser = argparse.ArgumentParser(description='Repackage and flatten the inherited classes in extension and base producing a Data Harmonizer friendly and non-reference versions of the custom schema')
    parser.add_argument('-c', '--custom_schema', dest="custom_schema", help="The custom schema that makes references to extension and base schemas", required=True,type=str)
    parser.add_argument('-w', '--work_directory', dest="work_dir", help="The main directory containing folders : Base, Extension, Custom", default=False,type=str)

    cli_input= parser.parse_args()

    if cli_input.work_dir:
    	work_dir=cli_input.work_dir
    else:
    	work_dir="/".join(cli_input.custom_schema.split("/")[:-3])

    reference_model=yaml_loader.load(cli_input.custom_schema, SchemaDefinition)
    updated_model=yaml_loader.load(cli_input.custom_schema, SchemaDefinition)

    mapping=generateBaseAndExtenstionMappings(reference_model,work_dir)
    cleanModel(updated_model)

    flattenInheritedProperties(reference_model,updated_model,mapping)
    dh_model=makeDataHarmonizerVersion(updated_model)

    yaml_dumper.dump(updated_model,cli_input.custom_schema.replace(".yaml","_full.yaml"))
    yaml_dumper.dump(dh_model,cli_input.custom_schema.replace(".yaml","_dh.yaml"))

    cleanNullValues(cli_input.custom_schema.replace(".yaml","_full.yaml"))
    cleanNullValues(cli_input.custom_schema.replace(".yaml","_dh.yaml"))

def cleanNullValues(yaml_file):
	### When none/null in python is written to YAML, value is interpreted a string. Quick regex replace to make value null
  with open (yaml_file, 'r' ) as f:
    content = f.read()
    content_new = content.replace("None","null")
  with open(yaml_file, 'w') as file:
    file.write(content_new)

def generateBaseAndExtenstionMappings(model,working_directory):
	"""
	Check through each class in Custom schema and map to appropriate import
	If import is base, no furhther action
	If import is extension, read model and find matching base
	Return mappings as a dictionary
	"""
	mapping={}

	for class_key in model.classes.keys():
		check=0
		for import_key in model.imports:
		###Match class name to appropriate import
			if class_key.lower() in import_key.lower():
			### If import is from base, match the base yaml file and class name
				if "base" in import_key:
					if os.path.isfile("%s/%s.yaml" % (working_directory,import_key)):
						mapping[class_key]={
						"base_import": "%s/%s.yaml" % (working_directory,import_key),
						"extension_import": None,
						"base_import_name": model.classes[class_key]['is_a'],
						"extension_import_name": None,
						}
					else:
						print("Error cannot find the following file : %s/%s.yaml" % (working_directory,import_key))
						exit(1)
				elif "extension" in import_key:
					if os.path.isfile("%s/%s.yaml" % (working_directory,import_key)):
						#print("%s/%s.yaml" % (working_directory,import_key))
						tmp_model=yaml_loader.load("%s/%s.yaml" % (working_directory,import_key), SchemaDefinition)
						### If import is from extension and base, match yaml and class names for both
						if len(tmp_model.imports)!=0:
							#print("%s yatzee B.A" % (import_key))
							mapping[class_key]={
							"base_import": "%s/%s.yaml" % (working_directory,tmp_model.imports[0]),
							"extension_import": "%s/%s.yaml" % (working_directory,import_key),
							"base_import_name": tmp_model.classes[model.classes[class_key]['is_a']]['is_a'],
							"extension_import_name": model.classes[class_key]['is_a'],
							}
						else:
							### If import is from extension only, match yaml and class names for extension
							#print("%s yatzee B.B" % (import_key))
							mapping[class_key]={
							"base_import": None,
							"extension_import": "%s/%s.yaml" % (working_directory,import_key),
							"base_import_name": None,
							"extension_import_name": model.classes[class_key]['is_a'],
							}
					else:
						print("Error cannot find the following file : %s/%s.yaml" % (working_directory,import_key))
						exit(1)
			else:
				check+=1

		if check==len(model.imports):
			print("Error cannot match class %s to any imports" % class_key)
			exit(1)

	return(mapping)

def cleanModel(model):
	"""
	Remove old imports and fill in with linkML:types
	"""
	model.prefixes['linkml']="https://w3id.org/linkml/"
	model.imports=['linkml:types']
	###Remove "is_a" inheritances
	for key in model.classes.keys():
	    #Remove is_a
	    del model.classes[key]['is_a']

	###return(model)

def flattenInheritedProperties(reference_model,updated_model,mapping):
	"""
	Traverse through each class importing base and extension slots,enums, and whatever else I can't think of at the moment because no coffee.
	"""
	for key in updated_model.classes.keys():
		###For base import, we want every property except empty ones and name
	    if mapping[key].get("base_import"):
	        #print("2 %s A" % (key))
	        tmp_model=yaml_loader.load(mapping[key]['base_import'], SchemaDefinition)
	        for base_property in tmp_model.classes[mapping[key]["base_import_name"]]:
	            #print(base_property)
	            if tmp_model.classes[mapping[key]["base_import_name"]][base_property]==None:
	                continue
	            if base_property=='name':
	                continue
	            #if base_property=='range':
	            #    print(base_property,mapping[key]['base_import'],tmp_model.classes[mapping[key]["base_import_name"]][base_property])
	            if len(tmp_model.classes[mapping[key]["base_import_name"]][base_property])!=0:
	                #print(key,base_property)
	                updated_model.classes[key][base_property]=tmp_model.classes[mapping[key]["base_import_name"]][base_property]

	        for slot_item in tmp_model['slots']:
	            updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
	            ### Conversion from YAML to python object stringifies Menu,None need to fix
	            if bool(re.search('^\\[.*\\]$', updated_model['slots'][slot_item]['range'])):
	            	#print("A",updated_model['slots'][slot_item]['range'])
	            	tmp_array=[]
	            	old_value=updated_model['slots'][slot_item]['range']
	            	if "None" in old_value:
	            		tmp_array.append("None")
	            	for val in re.findall("'.*'",old_value):
	            		tmp_array.append(val.replace("'",""))
	            	updated_model['slots'][slot_item]['range']=tmp_array
	            	#print("B",updated_model['slots'][slot_item]['range'])
	        for enum_item in tmp_model['enums']:
	            updated_model['enums'][enum_item]=tmp_model['enums'][enum_item]
	       
	    ### For extended without base imports, we also want every property except empty ones and name     
	    if mapping[key].get("extension_import") and not mapping[key].get("base_import"):
	        #print("2 %s B" % (key))
	        tmp_model=yaml_loader.load(mapping[key]['extension_import'], SchemaDefinition)
	        for base_property in tmp_model.classes[mapping[key]["extension_import_name"]]:
	            if tmp_model.classes[mapping[key]["extension_import_name"]][base_property]==None:
	                continue
	            if base_property=='name':
	                continue
	            if len(tmp_model.classes[mapping[key]["extension_import_name"]][base_property])!=0:
	                #print(key,base_property)
	                updated_model.classes[key][base_property]=tmp_model.classes[mapping[key]["extension_import_name"]][base_property]

	        for slot_item in tmp_model['slots']:
	            updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
	            ### Conversion from YAML to python object stringifies Menu,None need to fix
	            if bool(re.search('^\\[.*\\]$', updated_model['slots'][slot_item]['range'])):
	            	#print("A",updated_model['slots'][slot_item]['range'])
	            	tmp_array=[]
	            	old_value=updated_model['slots'][slot_item]['range']
	            	if "None" in old_value:
	            		tmp_array.append("None")
	            	for val in re.findall("'.*'",old_value):
	            		tmp_array.append(val.replace("'",""))
	            	updated_model['slots'][slot_item]['range']=tmp_array
	            	#print("B",updated_model['slots'][slot_item]['range'])
	        for enum_item in tmp_model['enums']:
	            updated_model['enums'][enum_item]=tmp_model['enums'][enum_item]
	    
	    ### For extended with base imports, b/c earlier base was imported, we only want to import news slots, definitions for new slots, enums related to new slots, and usage of new slots  
	    if mapping[key].get("extension_import") and mapping[key].get("base_import"):
	        #print("2 %s C" % (key))
	        tmp_model=yaml_loader.load(mapping[key]['extension_import'], SchemaDefinition) 
	        ###updated_model.classes[key]['slots']=updated_model.classes[key]['slots']+tmp_model.classes[mapping[key]["extension_import_name"]]['slots']
	        
	        ###Add slots defintions
	        for slot_item in tmp_model.classes[mapping[key]["extension_import_name"]]['slots']:
	          updated_model.classes[key]['slots'].append(tmp_model['slots'][slot_item]['name'])
	          updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
	          #print("A",slot_item,key,tmp_model['slots'][slot_item])
	          if bool(re.search('^\\[.*\\]$', tmp_model['slots'][slot_item]['range'])):
	              tmp_array=[]
	              current_value=tmp_model['slots'][slot_item]['range']
	              if "None" in old_value:
	                tmp_array.append("None")
	              for val in re.findall("'.*'",current_value):
	                tmp_array.append(val.replace("'",""))
	              updated_model['slots'][slot_item]['range']=tmp_array
	        for enum_item in tmp_model['enums']:
	            updated_model['enums'][enum_item]=tmp_model['enums'][enum_item]
		        #for slot_item in tmp_model['slots']:
		        #    updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
		        #for enum_item in tmp_model['enums']:
		        #    updated_model['enums'][enum_item]=tmp_model['enums'][enum_item]

	        if len(tmp_model['classes'][mapping[key].get("extension_import_name")]['slot_usage'])>0:
	            for slot_usage in tmp_model['classes'][mapping[key].get("extension_import_name")]['slot_usage']:
	                #print(slot_usage,key)
	                updated_model.classes[key]['slot_usage'][slot_usage]=tmp_model['classes'][mapping[key].get("extension_import_name")]['slot_usage'][slot_usage]

def makeDataHarmonizerVersion(model):
	"""
	Add dh_interface class (required for data harmonizer) and make every other class an instance of it
	"""

	dataharmonizer_version=copy.deepcopy(model)

	dataharmonizer_version.classes['dh_interface']=ClassDefinition(
		name="dh_interface",
		description="A DataHarmonizer interface",
		from_schema="https://example.com/base_schema.yaml"
	)

	for key in model.classes.keys():
		dataharmonizer_version.classes[key]['is_a']='dh_interface'



	return(dataharmonizer_version)



if __name__ == "__main__":
    main()
