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
import importlib
from datetime import date

version_to_version = {
  """
  Within each version to version, specify the following:
  - studies
  - analysisTypes
  - per analysisType the prior and current versions
  """
  "1.0to2.0" : {
    "studies" : [
        "PCGLST0001",
        "PCGLST0003",
        #"PCGLST0002"
    ],
    "analysisTypes" : {
      ###Prod values
      #"variantCall" : {"old":3.0, "new": 4.0},
      #"sequenceExperiment" : {"old":2.0, "new": 1.0},
      #"sequenceAlignment" : {"old":2.0, "new": 1.0}
      ###Dev
      "variantCall" : {"old":2.0, "new": 4.0},
      "sequenceExperiment" : {"old":1.0, "new": 2.0}, #78
      "sequenceAlignment" : {"old":1.0, "new": 4.0} #78
    }

  }
}

def check_url(url):
    """
    Check the health endpoint to ensure song can be reached.
    Exit if error
    """
    try:
        health_url="%s/isAlive" % (url)
        response = requests.get(health_url, timeout=5)
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

def retrieve_records(url,token,versions):
    """
    Sets up record collection for downstream interactions
    First - establishes record and corresponding keys for tracking initial records, modified, confirmed successes and failures
    Second - populates the "valid" and "unmodified" using SONG's pagination endpoint
    """
    records={}
    page_limit=1000
    for study in version_to_version.get(versions).get('studies'):
        records[study]={
            "valid":[],
            "invalid":{},
            "modified":[],
            "unmodified":{},
            "committed": {},
            "uncomitted": {},
            "verified" : {}
            }

        print(f"Retrieving records for study {study}")

        ###Return total first
        #https://file-manager.submission.genomelibrary.ca/studies/PCGLST0001/analysis/paginated?analysisStates=PUBLISHED&limit=10&offset=1
        get_total_url="%s/studies/%s/analysis/paginated?analysisStates=PUBLISHED&limit=10&offset=1" % (url,study)

        try:
            response = requests.get(get_total_url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5)
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
            total=response.json().get('totalAnalyses',None)
            if total is None:
                raise ValueError("totalAnalyses is null")
        except requests.exceptions.JSONDecodeError:
            raise SystemExit(f"{get_total_url}: Response was not valid JSON")
        except (KeyError, TypeError, ValueError) as e:
            raise SystemExit(f"{get_total_url}: Could not populate total ({e!r})")

        for page in range(0,total+page_limit,page_limit):
            get_analysis_url="%s/studies/%s/analysis/paginated?analysisStates=PUBLISHED&limit=%s&offset=%s" % (url,study,str(page_limit),str(page))

            try:
                response = requests.get(get_analysis_url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5)
                if response.status_code!=200:
                    raise SystemExit(f"Server response {response.status_code}")
                if 'analyses' not in response.json().keys():
                    raise SystemExit(f"Improperly formated response {response.status_code}")
            except requests.exceptions.Timeout:
                raise SystemExit(f"{get_total_url}: Timeout")
            except requests.exceptions.ConnectionError:
                raise SystemExit(f"{get_total_url}: Connection failed")
            except requests.exceptions.HTTPError as e:
                raise SystemExit(f"{get_total_url}: HTTP {e.response.status_code}, body: {e.response.text}")
            except requests.exceptions.RequestException as e:
                raise SystemExit(f"{get_total_url}: {e}")

            print(f"{study},parsing records #{page}/{total},{len(records[study]['valid'])} valid records, {len(records[study]['invalid'])} invalid records")
            for analysis in response.json()['analyses']:

                if analysis['analysisState']!="PUBLISHED":
                    records[study]['invalid'][analysis['analysisId']]="Not Published"
                elif analysis['analysisType']['name'] not in version_to_version.get(versions).get('analysisTypes').keys():
                    records[study]['invalid'][analysis['analysisId']]="Not a targeted analysis Type"
                elif analysis['analysisType']['version']!=version_to_version.get(versions).get('analysisTypes').get(analysis['analysisType']['name']).get("old"):
                    records[study]['invalid'][analysis['analysisId']]="Not a targeted analysis version"
                else:
                    records[study]['valid'].append(analysis)
        ###COMMENT THIS OUT FOR PRODUCTION - THIS IS TO LIMIT THE AMOUNT OF RECORDS MODIFIED IN DEV. DATA POVERTY.
        records[study]['valid']=records[study]['valid'][:2]
    return(records)

        
        
def modify_records(records,versions):
    """
    Apply changes to relevant records
    """
    local_module = importlib.import_module("migration%s" % (versions.replace('.','_')))
    return(local_module)

def unpublish_record(analysis,url,study,token,disable_dry_run):
    #PUT https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca/studies/ho/analysis/unpublish/hi
    url="%s/studies/%s/analysis/unpublish/%s" % (url,study,analysis['analysisId'])

    if disable_dry_run:
        print("...UNPUBLISHING",end="")
        try:
            response = requests.put(url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5)
            if response.status_code!=200:
                return(f"UNPUBLISH - Server response {response.status_code}")
        except Exception as e:
            return(f"UNPUBLISH - {type(e).__name__}: {e}")

        return(False)
    else:
        print("...UNPUBLISHING")
        print(url) 


            

def remove_contents_record(analysis,disable_dry_run):

    if disable_dry_run:
        print("...REMOVING",end="")
        try:
            for key in [
                "analysisId",
                "studyId",
                "analysisState",
                "createdAt",
                "updatedAt",
                "firstPublishedAt",
                "publishedAt",
                "analysisStateHistory",
                "files"
                ]:
                del analysis[key]

            del analysis['analysisType']['version']
        except Exception as e:
            return(f"REMOVING - {type(e).__name__}: {e}")
    else:
        print("...REMOVING")
        print("beep boop")
        return(False,False)

def update_record(analysis,url,study,token,disable_dry_run,original_analysis):
    #PUT https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca/studies/ho/analysis/hi
    url="%s/studies/%s/analysis/%s" % (url,study,original_analysis['analysisId'])

    if disable_dry_run:
        print("...UPDATING",end="")
        try:
            response = requests.put(url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5,json=analysis)
            if response.status_code!=200:
                return(f"UPDATING - Server response {response.status_code}")
        except Exception as e:
            return(f"UPDATING - {type(e).__name__}: {e}")

        return(False)
    else:
        print("...UPDATING")
        print(url)
        return(False,False)



def publish_record(analysis,url,study,token,disable_dry_run):
    #PUT https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca/studies/ho/analysis/publish/hi?ignoreUndefinedMd5=false
    url="%s/studies/%s/analysis/publish/%s?ignoreUndefinedMd5=false" % (url,study,analysis['analysisId'])

    if disable_dry_run:
        print("...PUBLISHING",end="")
        try:
            response = requests.put(url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5)
            if response.status_code!=200:
                return(f"PUBLISH - Server response {response.status_code}")
        except Exception as e:
            return(f"PUBLISH - {type(e).__name__}: {e}")

        return(False)
    else:
        print("...PUBLISHING")
        print(url)
        return(False,False)


def verify_record(analysis,url,study,token,disable_dry_run):
    #PUT https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca/studies/ho/analysis/publish/hi?ignoreUndefinedMd5=false
    url="%s/studies/%s/analysis/%s" % (url,study,analysis['analysisId'])

    if disable_dry_run:
        print("...VERIFYING")
        try:
            response = requests.get(url,headers={"Authorization" : "Bearer %s" % (token)},timeout=5)
            if response.status_code!=200:
                return(f"VERIFY - Server response {response.status_code}",False)
        except Exception as e:
            return(f"VERIFY - {type(e).__name__}: {e}",False)

        if response.json()['analysisState']=='PUBLISHED':
            return(False,True)
        return(False,False)
    else:
        print("...VERIFYING")
        print(url)
        return(False,False)



def commit_records(records,url,token,disable_dry_run):
    """
    Tracks SONG interactions - unpublish, remove, update, publish, verify
    UNPUBLISH - in case any production service is listening to SONG, allows any changes made to be re-indexed/picked up post publish
    REMOVE - For the update endpoint, not all fields in the SONG analysis fields are needed.
    UPDATE - run the UPDATE endpoint. Cannot use patch. Patch expects version to remain consistent.
    PUBLISH - See UNPUBLISH
    VERIFY - sanity check, ensures the record was successfully published.
    """
    #token="BOB"
    if not disable_dry_run:
        print("### Dry run enabled - Beep boop")

    for study in records.keys():
        for analysis in records[study]["modified"]:
            print("Working on %s %s" % (study,analysis['analysisId']),end="")
            tmp_analysis=copy.deepcopy(analysis)#analysis.copy()
            ### UNPUBLISH
            error=unpublish_record(tmp_analysis,url,study,token,disable_dry_run)

            if error:
                records[study]['uncomitted'][analysis['analysisId']]=error
                print("...ERR")
                continue

            ### Remove contents
            error=remove_contents_record(tmp_analysis,disable_dry_run)

            if error:
                records[study]['uncomitted'][analysis['analysisId']]=error
                print("...ERR")
                continue

            ### UPDATE
            error=update_record(tmp_analysis,url,study,token,disable_dry_run,analysis)

            if error:
                records[study]['uncomitted'][analysis['analysisId']]=error
                print("...ERR")
                continue

            ### PUBLISH
            error=publish_record(analysis,url,study,token,disable_dry_run)

            if error:
                records[study]['uncomitted'][analysis['analysisId']]=error
                print("...ERR")
                continue

            ### VERIFY
            error,success=verify_record(analysis,url,study,token,disable_dry_run)

            if error:
                records[study]['uncomitted'][analysis['analysisId']]=error
                print("...ERR")
                continue

            if success:
                records[study]['verified'][analysis['analysisId']]="Success"           


    return()

def main():
  """
  Migration script for song. Version and study dependent.

  Dry run example:
  python scripts/migration/song_migration/migrate.py \
    -t $token \
    -u https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca \
    -v "1.0to2.0"
  Live production example:
  python scripts/migration/song_migration/migrate.py \
    -t $token \
    -u https://file-manager.submission.gateway.dev.k8s.pcgl.dev-sd4h.ca \
    -v "1.0to2.0" \
    --disable_dry_run
  """
  parser = argparse.ArgumentParser(description='The script aims to migrate SONG entries')
  parser.add_argument('-t', '--token', dest="token", help="PCGL API Token", required=True,type=str)
  parser.add_argument('-u', '--url', dest="url", help="Song URL", required=True,type=str)
  parser.add_argument('-v', '--version_to_version', dest="versions", help="String to track version to version specific modification", required=True,type=str)
  parser.add_argument('--d', '--disable_dry_run', dest="disable_dry_run", help="Flag to force intentional commit",default=False,action="store_true")

  args = parser.parse_args()

  ###Check URL
  check_url(args.url)
  ###Load functions
  conversion=load_functions(args.versions)
  ###Retrieve records
  records=retrieve_records(args.url,args.token,args.versions)

  print ("# Status update - Post retrieval")
  for study in records.keys():
    print("### %s" % (study))
    for key in records[study]:
        print("##### %s : %s" % (key,len(records[study][key])))

  ###Modify records
  conversion.modify(records)

  print ("# Status update - Post modification")
  for study in records.keys():
    print("### %s" % (study))
    for key in records[study]:
        print("##### %s : %s" % (key,len(records[study][key])))

  ###Update and commit
  commit_records(records,args.url,args.token,args.disable_dry_run)

  print ("# Status update - Post commit")
  for study in records.keys():
    print("### %s" % (study))
    for key in records[study]:
        print("##### %s : %s" % (key,len(records[study][key])))

  ### Remove bulky records
  for study in records.keys():  
    for key in ["valid","modified"]:
        del records[study][key]

  ### Return results in JSON file
  with open(("%s_%s.json" % (date.today(),args.versions.replace('.','_'))), "w", encoding="utf-8") as file:
    json.dump(records, file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()