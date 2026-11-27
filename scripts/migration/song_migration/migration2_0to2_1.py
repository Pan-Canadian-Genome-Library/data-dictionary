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
import copy
import requests

def experiment_submitter_id_to_pcgl_ids(analysis,clinical_url,category,token,study):
    """
    Note the change was converting "submitter_experiment_id" to "submitter_experiment_ids".
    Originally the format was in string, so now have to convert to array of strings.
    """
    updated_record=copy.deepcopy(analysis)
    ###'https://submission.gateway.dev.k8s.pcgl.dev-sd4h.ca/data/category/4/organization/PCGLST0003/query?entityName=experiment'
    url="%s/data/category/%s/organization/%s/query?entityName=experiment" % (clinical_url,category,study)
    headers = {
        "accept": "application/json",
        "Authorization": "Bearer %s" % token,
        "Content-Type": "application/json",
    }

    payload = {
        "op": "and",
        "content": [
            {
                "op": "in",
                "content": {
                    "fieldName": "submitter_experiment_id",
                    "value": updated_record['submitter_experiment_ids'],
                },
            }
        ],
    }
    print(url)
    print(payload)
    try:
        response = requests.post(url, headers=headers, json=payload)
        pcgl_ids=[]
        print(response.status_code)
        if response.status_code!=200:
            return(False,updated_record,"Unable to fetch PCGL ids for record %s : %s" % (updated_record['analysisId']),response.status_code)
        
        for record in response.json()['records']:
            pcgl_ids.append(
                record['data']['pcgl_experiment_id']
            )

        if len(pcgl_ids)!=len(updated_record['submitter_experiment_ids']):
            return(False,updated_record,"Experiment records length does not match returned PCGL Id for record %s" % (updated_record['analysisId']))
        else:

            updated_record['pcgl_experiment_id']=pcgl_ids
            return(True,updated_record,None)
    except:   
            return(False,updated_record,"Unable to fetch PCGL ids for record %s" % (updated_record['analysisId']))


def modify(records,url,version_to_version,token):
    """
    Generic function to be called by migrate.py. Iterate through analyses applying modifications
    Takes records[study][valid] and modifies contents into records[study][modified]
    """
    for study in records.keys():
        for analysis in records[study]["valid"]:
            reasons=[]
            modified,updated_record,reason = experiment_submitter_id_to_pcgl_ids(
                analysis,url,
                version_to_version.get('studies').get(study),
                token,
                study
                )

            if not modified:
                reasons.append(reason)

            if modified:
                records[study]['modified'].append(updated_record)
            else:
                records[study]['unmodified'][analysis['analysisId']]=";".join(reasons)


    return()