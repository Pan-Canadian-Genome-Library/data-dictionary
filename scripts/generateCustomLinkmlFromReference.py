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
from linkml_runtime.linkml_model import SchemaDefinition, ClassDefinition, SlotDefinition, EnumDefinition, PermissibleValue, Example
from linkml_runtime.linkml_model.meta import AnonymousSlotExpression , ClassDefinition, SlotDefinition, ClassExpression, ClassDefinitionName, ClassRule, AnonymousClassExpression, SlotExpression, SlotDefinitionName, PresenceEnum

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

	#print("work_dir=%s"%work_dir)
	reference_model=yaml_loader.load(cli_input.custom_schema, SchemaDefinition)
	updated_model=yaml_loader.load(cli_input.custom_schema, SchemaDefinition)

	mapping=generateBaseAndExtenstionMappings(cli_input.custom_schema,reference_model,work_dir)
	print(mapping)
	cleanModel(updated_model)

	cleanVersion(updated_model,mapping)

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


def cleanVersion(updated_model,mapping):
	"""
	Combine versions from base schema and extensions schema to generate custom schema.
	Both version are in float "N.N" denoting major minor changes.
	Custom schema will be "A.a.B.b" denoting : Major base. Minor Base. Major Extension. Minor Extension.
	"""
	for key in updated_model.classes.keys():
		if mapping[key].get("base_import"):
			tmp_model=yaml_loader.load(mapping[key]['base_import'], SchemaDefinition)
			break

	base_version=re.search("^\\d.\\d", str(tmp_model.version))
	extension_version=re.search("^\\d.\\d", str(updated_model.version))

	if not bool(base_version):
		print('Error retrieve base version')

	if not bool(extension_version):
		print('Error retrieve extension version')

	updated_model.version="%s.%s" % (str(base_version[0]),str(extension_version[0]))


def generateBaseAndExtenstionMappings(custom_schema,model,working_directory):
	"""
	Check through each class in Custom schema and map to appropriate import
	If import is base, no furhther action
	If import is extension, read model and find matching base
	Return mappings as a dictionary
	"""
	mapping={}
	check=0
	for class_key in model.classes.keys():
		###Match class name to appropriate import
			### If import is from base, match the base yaml file and class name
			#print(class_key)
			#print(model.classes[class_key]['is_a'])
			if "base" in  model.classes[class_key]['is_a']:
				if os.path.exists("%s/base/base.yaml" % (working_directory)):
					mapping[class_key]={
					"base_import": "%s/base/base.yaml" % (working_directory),
					"extension_import": None,
					"base_import_name": model.classes[class_key]['is_a'],
					"extension_import_name": None,
					}
				else:
					print("Error cannot find the following file : %s/base/base.yaml" % (working_directory))
					exit(1)
			elif "extension" in  model.classes[class_key]['is_a']:
				if os.path.exists("%s/%s" % (working_directory, os.path.split(custom_schema)[0].replace("custom","extension"))):
					#print("%s/%s.yaml" % (working_directory,import_key))
					### If import is from extension and base, match yaml and class names for both
					class_key_path = "%s/%s.yaml"%(os.path.split(custom_schema)[0].replace("custom", "extension"), class_key.lower())
					tmp_model=yaml_loader.load(class_key_path, SchemaDefinition)
					if tmp_model.classes[model.classes[class_key]['is_a']]['is_a'] is not None:
						#print("%s yatzee B.A" % (import_key))
						mapping[class_key]={
						"base_import": "%s/base/base.yaml" % (working_directory),
						"extension_import": "%s/%s/%s.yaml" % (working_directory,os.path.split(custom_schema)[0].replace("custom","extension"),model.classes[class_key]['is_a'].split("_")[-1].lower()),
						"base_import_name": tmp_model.classes[model.classes[class_key]['is_a']]['is_a'],
						"extension_import_name": model.classes[class_key]['is_a'],
						}
					else:
						### If import is from extension only, match yaml and class names for extension
						#print("%s yatzee B.B" % (import_key))
						extension_name = "%s.yaml"%model.classes[class_key]['is_a'].split("_")[-1].lower()
						mapping[class_key]={
						"base_import": None,
						"extension_import": "%s/%s/%s" % (working_directory,os.path.split(custom_schema)[0].replace("custom","extension"),extension_name),
						"base_import_name": None,
						"extension_import_name": model.classes[class_key]['is_a'],
						}
				else:
					print("Error cannot find the following file : %s/%s.yaml" % (working_directory,class_key))
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
	for key in reference_model.classes.keys():
		###For base import, we want every property except empty ones and name
		print(key,mapping[key])
		if mapping[key].get("base_import"):
			#print("2 %s A" % (key),mapping[key]['base_import'])
			tmp_model=yaml_loader.load(mapping[key]['base_import'], SchemaDefinition)
			for base_property in tmp_model.classes[mapping[key]["base_import_name"]]:
				#print(base_property)
				if tmp_model.classes[mapping[key]["base_import_name"]][base_property]==None:
					continue
				if base_property=='name':
					continue
				#if base_property=='range':
				#	print(base_property,mapping[key]['base_import'],tmp_model.classes[mapping[key]["base_import_name"]][base_property])
				if len(tmp_model.classes[mapping[key]["base_import_name"]][base_property])!=0:
					#print(key,base_property)
					updated_model.classes[key][base_property]=tmp_model.classes[mapping[key]["base_import_name"]][base_property]

			for slot_item in tmp_model['slots']:
				updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
				### Conversion from YAML to python object stringifies Menu,None need to fix
				#print(slot_item)
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

		for slot_item in  updated_model['slots'].keys():
			print(slot_item)
			updated_model['slots'][slot_item]['title']=slot_item

		
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
				#print(slot_item)
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
				#	updated_model['slots'][slot_item]=tmp_model['slots'][slot_item]
				#for enum_item in tmp_model['enums']:
				#	updated_model['enums'][enum_item]=tmp_model['enums'][enum_item]

	for key in reference_model.classes.keys():
		usage={}
		main_slot_id=None
		slot_id=[]
		others=[]
		extensions=[]

		if mapping[key].get("extension_import_name") and mapping[key].get("base_import_name"):
			tmp_model=yaml_loader.load(mapping[key]['extension_import'], SchemaDefinition)
			for slot in updated_model.classes[key]['slots']:
				if slot.endswith("_id") and key in slot:
					main_slot_id=slot
				elif slot.endswith("_id"):
					slot_id.append(slot)
				elif slot in tmp_model.classes[mapping[key]["extension_import_name"]]['slots']:
					print("D",key,tmp_model.classes[mapping[key]["extension_import_name"]]['slots'])
					extensions.append(slot)
				else:
					others.append(slot)
			slot_id.sort()
			others.sort()
			extensions.sort()
			if main_slot_id:
				usage[main_slot_id]=SlotDefinition(name=main_slot_id,rank=1,slot_group="Database Identifiers")
			if len(slot_id)>0:
				for slot in slot_id:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group="Database Identifiers")
			if len(others)>0:
				for slot in others:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group=key)
			if len(extensions)>0:
				for slot in extensions:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group="Extensions %s" % (key))
		elif mapping[key].get("extension_import_name"):
			tmp_model=yaml_loader.load(mapping[key]['extension_import'], SchemaDefinition)
			for slot in updated_model.classes[key]['slots']:
				if slot.endswith("_id") and key in slot:
					main_slot_id=slot
				elif slot.endswith("_id"):
					slot_id.append(slot)
				elif slot in tmp_model.classes[mapping[key]["extension_import_name"]]['slots']:
					extensions.append(slot)
			slot_id.sort()
			others.sort()
			if main_slot_id:
				usage[main_slot_id]=SlotDefinition(name=main_slot_id,rank=1,slot_group="Database Identifiers")
			if len(slot_id)>0:
				for slot in slot_id:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group="Database Identifiers")
			if len(extensions)>0:
				for slot in extensions:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group="Extensions %s" % (key))
		else : 
			for slot in updated_model.classes[key]['slots']:
				if slot.endswith("_id") and key in slot:
					main_slot_id=slot
				elif slot.endswith("_id"):
					slot_id.append(slot)
				else:
					others.append(slot)
			slot_id.sort()
			others.sort()
			if main_slot_id:
				usage[main_slot_id]=SlotDefinition(name=main_slot_id,rank=1,slot_group="Database Identifiers")
			if len(slot_id)>0:
				for slot in slot_id:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group="Database Identifiers")
			if len(others)>0:
				for slot in others:
					usage[slot]=SlotDefinition(name=slot,rank=len(usage.keys())+1,slot_group=key)
		print("C",key,usage)
		updated_model.classes[key]['slot_usage']=usage

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
