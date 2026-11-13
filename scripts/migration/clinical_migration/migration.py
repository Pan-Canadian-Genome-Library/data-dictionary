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
import io
import random
import jsonschema
import string
import time
import random
import hashlib
import shutil
import argparse
import copy
import importlib
from datetime import datetime
import pandas as pd
import math

"""
Within each version to version, specify the following:
- studies
- analysisTypes
- per analysisType the prior and current versions
"""
# version_to_version = {
#   "1.1to2.0" : {
#     "studies" : {
#         "PCGLST0003": {"category":4,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
#         "PCGLST0037": {"category":37,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
#         #"PCGLST0001" : {"category":1,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
#         #"PCGLST0003" : {"category":1,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]}
#     }
#   }
# }

### staging
version_to_version = {
  "1.1to2.0" : {
    "studies" : {
        "PCGLST0111": {"category":141,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"],"submit":["participant","demographic","sociodemographic"]},
        # "PCGLST0002": {"category":37,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
        # "PCGLST0003": {"category":72,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
        # "PCGLST0005": {"category":39,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
        # "PCGLST0007": {"category":107,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
        # "PCGLST0039": {"category":73,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]},
        # "PCGLST0040": {"category":74,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]}
        #"PCGLST0003" : {"category":1,"old":1.1, "new": 2.0,"entities": ["participant","demographic","sociodemographic"]}
    }
  }
}

def check_url(url):
    """
    Check the health endpoint to ensure song can be reached.
    Exit if error
    """
    try:
        health_url="%s/health" % (url)
        response = requests.get(health_url, timeout=20)
        response.raise_for_status()
        print(f"{url} connection successful")

    except requests.exceptions.Timeout:
        raise SystemExit(f"{health_url}: Timeout")
    except requests.exceptions.ConnectionError:
        raise SystemExit(f"{health_url}: Connection failed")
    except requests.exceptions.HTTPError as e:
        raise SystemExit(f"{health_url}: HTTP {e.response.status_code}, body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        raise SystemExit(f"{health_url}: {e}")
    
def load_functions(version):
    """
    Based on the version to version string arguement provided
    Finds the corresponding module.
    Module named as migration{VERSION}to{VERSION}.py. {Version} in float and "." replaced with "_"
    """
    if version not in version_to_version.keys():
        raise SystemExit(f"{version} is an invalid key")
    #print(records)

    #local_module = importlib.import_module("/Users/esu/Desktop/GitHub/pcgl/data-dictionary/scripts/migration/song_migration/migration1dot0to2dot0.py")
    local_module = importlib.import_module("migration%s" % (version.replace('.','_')))
    return(local_module)

def retrieve_records(url,token,versions,record_limit):
    """
    Sets up record collection for downstream interactions
    First - establishes record and corresponding keys for tracking initial records, modified, confirmed successes and failures
    Second - populates the "valid" and "invalid"
    """
    records={}
    page_limit=1000
    for study in version_to_version.get(versions).get('studies'):
        records[study]={
            "valid":{},
            "invalid":{},
            "modified":{},
            "unmodified":{},
            "submission" : {},
            "validation" : {}
            }

        print(f"Retrieving records for study {study}")

        ###Return total first
        #https://submission.gateway.staging.k8s.pcgl.dev-sd4h.ca/data/category/37/organization/PCGLST0002?entityName=participant&page=1&pageSize=1&view=flat
        category=str(version_to_version.get(versions).get('studies').get(study).get("category"))
        entities="&".join(["entityName="+z for z in version_to_version.get(versions).get('studies').get(study).get("entities")])
        get_total_url="%s/data/category/%s/organization/%s?%s&page=1&pageSize=%s&view=flat" % (url,category,study,entities,page_limit)

        print(get_total_url)
        try:
            response = requests.get(get_total_url,headers={"Authorization" : "Bearer %s" % (token)},timeout=20)
            if response.status_code!=200:
                raise SystemExit(f"Server response {response.status_code}")
        except requests.exceptions.Timeout:
            raise SystemExit(f"{get_total_url}: Timeout")
        except requests.exceptions.ConnectionError:
            raise SystemExit(f"{get_total_url}: Connection failed")
        except requests.exceptions.HTTPError as e:
            raise SystemExit(f"{get_total_url}: HTTP {e.response.status_code}, body: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise SystemExit(f"{get_total_url}: {e}")

        try:
            ###Return number of pages
            total=response.json().get('pagination',None).get('totalRecords',None)
            total_pages=response.json().get('pagination',None).get('totalPages',None)
            if total is None:
                raise ValueError("totalAnalyses is null")
        except requests.exceptions.JSONDecodeError:
            raise SystemExit(f"{get_total_url}: Response was not valid JSON")
        except (KeyError, TypeError, ValueError) as e:
            raise SystemExit(f"{get_total_url}: Could not populate total ({e!r})")

        ###Based on number of pages, iterate through pulling # of records
        for page in range(1,total_pages+1,1):
            get_records_url="%s/data/category/%s/organization/%s?%s&page=%s&pageSize=%s&view=flat" % (url,category,study,entities,page,str(page_limit))
            
            print(get_records_url)
            try:
                response = requests.get(get_records_url,headers={"Authorization" : "Bearer %s" % (token)},timeout=20)
                if response.status_code!=200:
                    raise SystemExit(f"Server response {response.status_code}")
                if 'records' not in response.json().keys():
                    raise SystemExit(f"Improperly formated response {response.status_code}")
            except requests.exceptions.Timeout:
                raise SystemExit(f"{get_total_url}: Timeout")
            except requests.exceptions.ConnectionError:
                raise SystemExit(f"{get_total_url}: Connection failed")
            except requests.exceptions.HTTPError as e:
                raise SystemExit(f"{get_total_url}: HTTP {e.response.status_code}, body: {e.response.text}")
            except requests.exceptions.RequestException as e:
                raise SystemExit(f"{get_total_url}: {e}")

            for record in response.json().get('records'):
                ###Triage record according to validation status
                if record.get('isValid'):
                    if record.get('entityName') not in records[study]['valid']:
                        records[study]['valid'][record.get('entityName')]={}

                    records[study]['valid'][record.get('entityName')][record['systemId']]=record
                else:
                    if record.get('entityName') not in records[study]['invalid']:
                        records[study]['invalid'][record.get('entityName')]={}

                    records[study]['invalid'][record.get('entityName')][record['systemId']]=record

            valid_counts, invalid_counts = ({name: len(lst) for name, lst in records[study][cat].items()} for cat in ('valid', 'invalid'))
            print(f"{study},parsing records #{page*page_limit}/{total}, valid records : {valid_counts}, invalid records: {invalid_counts}")
    return(records)

        
        
def modify_records(records,versions):
    """
    Apply changes to relevant records
    """
    local_module = importlib.import_module("migration%s" % (versions.replace('.','_')))
    return(local_module)

def make_tsvs(records):
    """
    Converts records to pandas TSVs. Also if items are lists join using "|" as strings
    """
    tsv={}
    for study in records.keys():
        if "modified" in records[study]:
            for entity in records[study]['modified']:
                if study not in tsv.keys():
                    tsv[study]={}

                sanitizing=[]
                for record in records[study]['modified'][entity].keys():
                    data={key: "|".join(item) if isinstance(item, list) else item for key,item in records[study]['modified'][entity][record]['data'].items()}
                    data['systemId']=records[study]['modified'][entity][record]['systemId']
                    sanitizing.append(data)
                tsv[study][entity]=pd.json_normalize(sanitizing)
    return(tsv)
                
def fix_sociodemographic(tsvs):
    """
    Add missing column
    """
    for study in tsvs.keys():
        if "sociodemographic" in tsvs[study].keys():
            if "geographical_location" not in tsvs[study]["sociodemographic"]:
                tsvs[study]['sociodemographic']['geographic_location_additional']=np.nan

def remove_pcgl_ids(tsvs):
    """
    remove PCGL ids otherwise lyric will complain
    """
    for study in tsvs.keys():
        for entity in tsvs[study].keys():
            for col in tsvs[study][entity]:
                if col.startswith("pcgl") and col.endswith("_id"):
                    tsvs[study][entity].drop(columns=col,inplace=True)


def submit_modification(url,tsvs,category,token,study):
    """
    Send batch TSVs 
    """
    modify_url="%s/submission/category/%s/data" % (url,category)

    headers={
    "accept": "application/json",
    "Authorization": f"Bearer {token}",
    }

    files = [
    ("files", (entity+".tsv", io.BytesIO(df.head().to_csv(sep="\t", index=False).encode("utf-8")), "text/tab-separated-values"))
    #("files", (entity+".tsv", io.BytesIO(df.head().to_csv(sep="\t", index=False).encode("utf-8")), "text/tab-separated-values"))
    for entity, df in tsvs.items()
    ]
    data = {"organization": study}

    try:
        response = requests.put(modify_url, headers=headers, files=files, data=data, timeout=60)
        if response.status_code!=200:
            return(None,f"{modify_url} : Server response {response.status_code}")
        if 'submissionId' not in response.json().keys():
            return(None,f"{modify_url} : Improperly formated response {response.status_code}")
    except requests.exceptions.Timeout:
        return(None,f"{modify_url} : Timeout")
    except requests.exceptions.ConnectionError:
        return(None,f"{modify_url} : Connection failed")
    except requests.exceptions.HTTPError as e:
        return(None,f"{modify_url} :  HTTP {e.response.status_code}, body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        return(None,f"{modify_url} : {e}")

    print("HELLO",response.json()['batchErrors'])

    return(
        response.json()['submissionId'],
        response.json()['batchErrors'] if len(response.json()['batchErrors'])>0 else None
        )

def verify_submission(url,category,token,study,submission_id):
    """
    Return submission status
    """
    get_url="%s/submission/%s" % (url,submission_id)

    headers={
    "accept": "application/json",
    "Authorization": f"Bearer {token}",
    }
    time.sleep(30)
    try:
        response = requests.get(get_url, headers=headers,timeout=60)
        if response.status_code!=200:
            return(None,f"{get_url} : Server response {response.status_code}")
        if 'errors' not in response.json().keys():
            return(None,f"{get_url} : Improperly formated response {response.status_code}")
    except requests.exceptions.Timeout:
        return(None,f"{get_url} : Timeout")
    except requests.exceptions.ConnectionError:
        return(None,f"{get_url} : Connection failed")
    except requests.exceptions.HTTPError as e:
        return(None,f"{get_url} :  HTTP {e.response.status_code}, body: {e.response.text}")
    except requests.exceptions.RequestException as e:
        return(None,f"{get_url} : {e}")

    status=response.json()['status']

    if status!='VALID':
        print(status)
        return(status,fetch_errors(url,token,submission_id,response.json()['data']['total']))
    else:
        return(status,None)

def fetch_errors(url,token,submission_id,total_records):
    """
    If errors are present, grab the errors
    """
    print("fetching errors")
    page_limit=1000
    headers={
    "accept": "application/json",
    "Authorization": f"Bearer {token}",
    }
    errors=[]

    for page in range(1,math.ceil(total_records/page_limit)+1):
        get_url="%s/submission/%s/details?page=%s&pageSize=%s" % (url,submission_id,page,page_limit)
        print(get_url)
        try:
            response = requests.get(get_url, headers=headers,timeout=60)
            if response.status_code!=200:
                print("AAAA?")
                return(f"{get_url} : Server response {response.status_code}")
            if 'data' not in response.json().keys():
                print("AAAA2?")
                return(f"{get_url} : Improperly formated response {response.status_code}")
        except requests.exceptions.Timeout:
            return(f"{get_url} : Timeout")
        except requests.exceptions.ConnectionError:
            return(f"{get_url} : Connection failed")
        except requests.exceptions.HTTPError as e:
            return(f"{get_url} :  HTTP {e.response.status_code}, body: {e.response.text}")
        except requests.exceptions.RequestException as e:
            return(f"{get_url} : {e}")

        #print(len(response.json()['errors']))
        for error in response.json()['errors']:
            errors.append(error)
        #print(len)

    if len(errors)>0:
        #print(errors)
        return(summarize_errors(errors))
    else:
        return(None)


def summarize_errors(errors):
    """
    If errors are present, summarizes by collecting by error type and field
    """
    print("summarizing errors")
    summary_errors={}

    for error in errors:
        if error['fieldName'] not in summary_errors:
            summary_errors[error['fieldName']]={}

        if error['reason'] not in summary_errors[error['fieldName']]:
            print(error)
            summary_errors[error['fieldName']][error['reason']]={
                "error_counts":1,
                "message": error.get('errors')[0].get('messsage',None) if "errors" in error.keys() else None ,
                "fieldValue": [error.get('fieldValue',None)]
            }

        summary_errors[error['fieldName']][error['reason']]['error_counts']+=1
        summary_errors[error['fieldName']][error['reason']]['fieldValue'].append(error.get('fieldValue',None))

    return(summary_errors)
def main():
  """
  Migration script for Clinical Data. Version and study dependent. Will only modify invalid records. Expectation is that a new dictionary verison has been deployed triggering a migration making records invalid.
  Will proceed with running modification up until commit step. Use the commit endpoint to finalize modifications
  Example run:
  python scripts/migration/clinical_migration/migration.py  \
    -t ${token} \
    -u https://submission.gateway.staging.k8s.pcgl.dev-sd4h.ca \
    -v "1.1to2.0"

  

  Generates two files:
  2026-11-04_14:54:11_1_0to2_0.json ### Tracks migration progress including successes and failures

  026-11-04_14:54:11_1_0to2_0.json Contents:
  Per study lists:
    - "valid" : Existing records that do not need to be touched.
    - "invalid": Existing record that qualify for migration e.g. incorrect analysisType, version, UNPUBLISHED
    - "unmodified": Existing records that failed modification
    - "submission": Tracks and returns errors due to batch submission or individual record submission
    - "validation": Tracks and returns status of batch submission
  """
  parser = argparse.ArgumentParser(description='The script aims to migrate SONG entries')
  parser.add_argument('-t', '--token', dest="token", help="PCGL API Token", required=True,type=str)
  parser.add_argument('-u', '--url', dest="url", help="Song URL", required=True,type=str)
  parser.add_argument('-v', '--version_to_version', dest="versions", help="String to track version to version specific modification", required=True,type=str)
  parser.add_argument('-n', '--record_limit', dest="record_limit", help="Enforce a record limit per study. Default 0.",default=0,type=int)
  parser.add_argument('-d', '--disable_dry_run', dest="disable_dry_run", help="Flag to force intentional commit",default=False,action="store_true")

  args = parser.parse_args()

  ###Check URL
  check_url(args.url)
  ###Load functions
  conversion=load_functions(args.versions)
  ###Retrieve records
  records=retrieve_records(args.url,args.token,args.versions,args.record_limit)

  print ("# Status update - Post retrieval")
  for study in records.keys():
    print("### %s" % (study))
    for key in records[study].keys():
        for entity in records[study][key]:
            print("##### %s %s : %s" % (key,entity,len(records[study][key][entity])))

  ###Modify records
  conversion.modify(records)
  print ("# Status update - Post modification")
  for study in records.keys():
    print("### %s" % (study))
    for key in records[study].keys():
        for entity in records[study][key]:
            print("##### %s %s : %s" % (key,entity,len(records[study][key][entity])))

  ###Convert records to TSV
  submittable_tsvs=make_tsvs(records)

  ###Minor fixes to appeaase Lyric
  fix_sociodemographic(submittable_tsvs)
  remove_pcgl_ids(submittable_tsvs)

  ###Write to disk
  for study in submittable_tsvs.keys():
      for entity in submittable_tsvs[study].keys():
          file_name="%s_%s.tsv" % (study,entity)
          submittable_tsvs[study][entity].to_csv(file_name, encoding="utf-8",sep='\t',index=False) 

  ###Submit modifications
  for study in submittable_tsvs.keys():

      submission_id,batch_errors=submit_modification(
          args.url,
          {entity:df for entity,df in submittable_tsvs[study].items() if entity in version_to_version[args.versions]["studies"][study]["submit"] },
          version_to_version[args.versions]["studies"][study]['category'],
          args.token,
          study
          )

      records[study]['submission']['submission_id']=submission_id
      records[study]['submission']['batch_errors']=batch_errors

  ###Verify submission status
  for study in submittable_tsvs.keys():
    if records[study]['submission']['submission_id']!=None:
        status,errors=verify_submission(
            args.url,
            version_to_version[args.versions]["studies"][study]['category'],
            args.token,
            study,
            records[study]['submission']['submission_id']
        )

        records[study]['validation']['submission_id']=submission_id
        records[study]['validation']['errors']=errors

  ### Return results in JSON file
  file_name=("%s_%s_%s.json" % (datetime.now().strftime("%Y-%m-%d"),datetime.now().strftime("%H:%M:%S"),args.versions.replace('.','_')))
  with open(file_name, "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4, ensure_ascii=False)
  print(file_name)

if __name__ == "__main__":
    main()