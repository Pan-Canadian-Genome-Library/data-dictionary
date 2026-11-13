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
import re

def remove_duo(record):
    """
    Remove duo codes
    """
    updated_record=copy.deepcopy(record)
    for col in ['duo_modifier','duo_permission','disease_specific_modifier']:
        try:
            if col in updated_record['data'].keys():
                del updated_record['data'][col]
        except:
            return(False,updated_record,"Unable to remove '%s' in record %s" % (col,record))

    return(True,updated_record,None)

def  remove_demographic_fields(record):
    """
    Remove duo codes
    """
    updated_record=copy.deepcopy(record)
    for col in ["age_at_death","age_at_enrollment","cause_of_death","vital_status"]:
        try:
            if col in updated_record['data'].keys():
                del updated_record['data'][col]
        except:
            return(False,updated_record,"Unable to remove '%s' in record %s" % (col,record))

    return(True,updated_record,None)

def find_participant_record(record,records,study,entity):
    #print(records[study]['valid']['demographic'][record]['data'].get("pcgl_participant_id"))
    try:
        participant_id=records[study]['invalid'][entity][record]['data'].get("pcgl_participant_id")
        for query_record in records[study]['modified']['participant'].keys():
            #print(participant_id,query_record['data'].get("pcgl_participant_id"))
            #print(participant_id)
            #print(records[study]['modified']['participant'][query_record]['data'].get("pcgl_participant_id"))
            #print(participant_id==records[study]['modified']['participant'][query_record]['data'].get("pcgl_participant_id"))
            if participant_id==records[study]['modified']['participant'][query_record]['data'].get("pcgl_participant_id"):
                return(True,query_record,None)

        return(False,None,"Unable to identify particpant ID related to record '%s'" % (record))
    except:
        return(False,None,"Unable to identify particpant ID related to record '%s'" % (record))

def copy_demographic_fields(record,participant_record,records,study):
    """
    copying over demographic fields. B/c they're all optional
    """
    #print(records[study]['valid']['demographic'][record][col])
    for col in ["age_at_death","age_at_enrollment","cause_of_death","vital_status"]:
        #print(study,records[study]['invalid'].keys())
        if col in records[study]['invalid']['demographic'][record]['data'].keys():
            records[study]['modified']['participant'][participant_record]['data'][col]=records[study]['invalid']['demographic'][record]['data'][col]

    # if len(error)>0:
    #     return(False,";".join(error))
    # else:
    #     return(True,None)

def copy_sociodemographic_fields(record,participant_record,records,study):
    for col in ["sex_at_birth","sex_collect_method","sex_another_category"]:
        error=[]
        try:
            if col in records[study]['invalid']['sociodemographic'][record]['data'].keys():
                records[study]['modified']['participant'][participant_record]['data'][col]=records[study]['invalid']['sociodemographic'][record]['data'][col]

                ###Edge case where "Other" is replaced by "Another method of collection"
                if records[study]['modified']['participant'][participant_record]['data'][col]=="Other":
                    records[study]['modified']['participant'][participant_record]['data'][col]="Another method of collection"

        except:
            error.append("Unable add demographic field %s to particpant ID %s and record '%s'" % (col,participant_record,record))

    if len(error)>0:
        return(False,";".join(error))
    else:
        return(True,None)

def add_sociodemographic_required_fields(record,records,study):
    error=[]
    updated_record=copy.deepcopy(records[study]['invalid']['sociodemographic'][record])
    for col in ["date_of_birth","date_of_birth_collection_method","total_income","total_income_collect_method"]:
        try:
            updated_record['data'][col]="Missing - Not provided"
        except:
            error.append("Unable add demographic field %s to record '%s'" % (col,record))

    if len(error)>0:
        return(False,";".join(error))
    else:
        records[study]['modified']['sociodemographic'][record]=updated_record
        return(True,None)
    
def fix_sociodemographic_values(record,records,study):
    error=[]

    updated_record=copy.deepcopy(records[study]['modified']['sociodemographic'][record])

    ### Updated enum from "Not applicable" to  "Missing - Not applicable"
    print([z for z in updated_record['data'].keys()])
    for col in updated_record['data'].keys():
        try:
            if isinstance(updated_record['data'][col],str):
                if updated_record['data'][col]=="Not applicable":
                    updated_record['data'][col]="Missing - Not applicable"
            elif isinstance(updated_record['data'][col],list):
                for ind,val in enumerate(updated_record['data'][col]):
                    if val=="Not applicable":
                        updated_record['data'][col][ind]="Missing - Not applicable"
        except:
            error.append("Unable update field %s to from 'Not applicable' to  Missing - Not applicable' in record '%s'" % (col,record))
            #error.append(f"Unable to update field {col} in record '{record}': {type(e).__name__}: {e}")
    ### Reduce sociodem_date_collection resolution to YYYY
    if 'sociodem_date_collection' in updated_record['data'].keys():
        if re.search(r"\d{4}-\d{2}-\d{2}||\d{4}-\d{2}", updated_record['data']['sociodem_date_collection']):
            try:
                updated_record['data']['sociodem_date_collection']=re.findall(r"\d{4}",updated_record['data']['socidem_date_collection'])[0]
            except Exception as e:
                    SystemExit(f'{e}')
            #except:
            #    error.append("Unable update field 'socidem_date_collection' to 'YYYY" % (col,record))

    ### Need clarification should this info move to total_income?
    if 'personal_income_collect_method' in updated_record['data'].keys():
        if  updated_record['data']['personal_income_collect_method']=="Self-identified" or updated_record['data']['personal_income_collect_method']=="Derived":
            try:
                updated_record['data']['personal_income_collect_method']="Missing - Not applicable"
            except:
                error.append("Unable make %s into Missing - Not applicable' in record '%s'" % (col,record))                

    ### Data generation error 
    if  updated_record['data']['ethnicity']!="Another Ethnic or Cultural Origin":
        if "ethnicity_another_category" in updated_record['data'].keys():
            if updated_record['data']["ethnicity_another_category"]!=None:
                try:
                    del updated_record['data']["ethnicity_another_category"]
                except:
                    error.append("Unable to remove field %s to from record '%s'" % (col,record))  

    if len(error)>0:
        return(False,";".join(error))
    else:
        records[study]['modified']['sociodemographic'][record]=updated_record
        return(True,None)


def modify(records):
    """
    Generic function to be called by migrate.py. Iterate through analyses applying modifications
    Takes records[study][invalid] and modifies contents into records[study][modified]
    """

    for study in records.keys():
        if "participant" in records[study]["invalid"].keys():
            records[study]["modified"]["participant"]={}
            records[study]["unmodified"]["participant"]={}
            for record in records[study]["invalid"]['participant'].keys():
                modified,updated_record,error=remove_duo(records[study]["invalid"]['participant'][record])

                if modified:
                    records[study]["modified"]['participant'][record]=updated_record
                    #print(updated_record)
                else:
                    records[study]["unmodified"]['participant'][record]=error
                    #print(error)

        ### This assumes participant is already in ingested in modified
        if "demographic" in records[study]["invalid"].keys():
            records[study]["unmodified"]["demographic"]={}
            records[study]["modified"]["demographic"]={}
            for record in records[study]["invalid"]['demographic'].keys():
                found,participant_record,error=find_participant_record(record,records,study,"demographic")            

                if not found:
                    if record in records[study]["unmodified"]['demographic'].keys():
                        records[study]["unmodified"]['demographic'][record]+=error
                    else:
                        records[study]["unmodified"]['demographic'][record]=error
                    continue

                #success,error=copy_demographic_fields(record,participant_record,records,study)
                copy_demographic_fields(record,participant_record,records,study)

                modified,updated_record,error=remove_demographic_fields(records[study]["invalid"]['demographic'][record])
                if modified:
                    records[study]["modified"]['demographic'][record]=updated_record
                    #print(updated_record)
                else:
                    records[study]["unmodified"]['demographic'][record]=error


     
        ### This assumes participant is already in ingested in modified
        if "sociodemographic" in records[study]["invalid"].keys():
            records[study]["unmodified"]["sociodemographic"]={}
            records[study]["modified"]["sociodemographic"]={}
            for record in records[study]["invalid"]['sociodemographic'].keys():
                found,participant_record,error=find_participant_record(record,records,study,"sociodemographic")            

                if not found:
                    if record in records[study]["unmodified"]['sociodemographic'].keys():
                        records[study]["unmodified"]['sociodemographic'][record]+=error
                    else:
                        records[study]["unmodified"]['sociodemographic'][record]=error
                    continue

                success,error=copy_sociodemographic_fields(record,participant_record,records,study)

                if not success:
                    if participant_record in records[study]["unmodified"]['participant'].keys():
                        records[study]["unmodified"]['participant'][participant_record]+=error
                    else:
                        records[study]["unmodified"]['participant'][participant_record]=error
                    continue


                success,error=add_sociodemographic_required_fields(record,records,study)
                if not success:
                    if record in records[study]["unmodified"]['sociodemographic'].keys():
                        records[study]["unmodified"]['sociodemographic'][record]+=error
                    else:
                        records[study]["unmodified"]['sociodemographic'][record]=error
                    continue

                success,error=fix_sociodemographic_values(record,records,study)
                if not success:
                    if record in records[study]["unmodified"]['sociodemographic'].keys():
                        records[study]["unmodified"]['sociodemographic'][record]+=error
                    else:
                        records[study]["unmodified"]['sociodemographic'][record]=error
                    continue

    return()