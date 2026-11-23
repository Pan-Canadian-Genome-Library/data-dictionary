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

def remove_demographic_fields(record):
    """
    Remove demographic fields. Hostseq still maintains demographic records as an extension so will have to alter them accordingly.
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
    """
    Using PCGL ID find the corresponding participant record to the entity record in question
    """
    try:
        participant_id=records[study]['invalid'][entity][record]['data'].get("pcgl_participant_id")
        for query_record in records[study]['modified']['participant'].keys():
            if participant_id==records[study]['modified']['participant'][query_record]['data'].get("pcgl_participant_id"):
                return(True,query_record,None)

        return(False,None,"Unable to identify particpant ID related to record '%s'" % (record))
    except:
        return(False,None,"Unable to identify particpant ID related to record '%s'" % (record))

def copy_demographic_fields(record,participant_record,records,study):
    """
    copying over demographic fields. B/c they're all optional
    """
    for col in ["age_at_death","age_at_enrollment","cause_of_death","vital_status"]:
        if col in records[study]['invalid']['demographic'][record]['data'].keys():
            records[study]['modified']['participant'][participant_record]['data'][col]=records[study]['invalid']['demographic'][record]['data'][col]


def copy_sociodemographic_fields(record,participant_record,records,study):
    """
    Copying existing nonsentiive sociodemographic date to participant record
    """
    error=[]
    for col in ["sex_at_birth","sex_collect_method","sex_another_category"]:

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
    """
    New required fields. Setting default to "Missing - Not Provided"
    """
    error=[]
    updated_record=copy.deepcopy(records[study]['invalid']['sociodemographic'][record])
    for col in ["date_of_birth_collection_method","total_income","total_income_collect_method"]:
        try:
            updated_record['data'][col]="Missing - Not provided"
        except:
            error.append("Unable add sociodemographic field %s to record '%s'" % (col,record))

    ###Use case, certain studies submitted DOB as 'dob_year' and 'dob_month', collect in new field or return as not provided
    col="date_of_birth"
    month_to_num = {
    "January": "01", "February": "02", "March": "03", "April": "04",
    "May": "05", "June": "06", "July": "07", "August": "08",
    "September": "09", "October": "10", "November": "11", "December": "12",
    }

    try:
        if "dob_year" in updated_record['data']:
            if "dob_month" in updated_record['data']:
                if updated_record['data']["dob_month"]=="Don't know":
                    date="%s" % (updated_record['data']["dob_year"])
                else:
                    date="%s-%s" % (updated_record['data']["dob_year"],month_to_num[updated_record['data']["dob_month"]])
            else:
                date="%s" % (updated_record['data']["dob_year"])
        else :
            date="Missing - Not provided"

        updated_record['data'][col]=date
    except:
        error.append("Unable to update field %s for record '%s'" % (col,record))    

    if len(error)>0:
        return(False,";".join(error))
    else:
        records[study]['modified']['sociodemographic'][record]=updated_record
        return(True,None)
    
def fix_sociodemographic_values(record,records,study):
    """
    Broader category of fixing sociodemographic values. Some are important such as the migration from "Not Applicable" to "Missing - Not Applicable" and sociodem date resolution to YYYY
    Other errors reflect staging data but are not consequential to Production (see individual comments)
    """
    error=[]

    updated_record=copy.deepcopy(records[study]['modified']['sociodemographic'][record])

    ### Updated enum from "Not applicable" to  "Missing - Not applicable"
    #print([z for z in updated_record['data'].keys()])
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

    ### Reduce sociodem_date_collection resolution to YYYY
    col='sociodem_date_collection'
    if col in updated_record['data'].keys():
        if "Missing" not in  updated_record['data'][col]:
            if re.search(r"\d{4}-\d{2}-\d{2}||\d{4}-\d{2}", updated_record['data'][col]):
                try:
                    updated_record['data'][col]=re.findall(r"\d{4}",updated_record['data'][col])[0]
                except:
                    error.append("Unable update field '%s' to 'YYYY' for record %s" % (col,record))

    ### Need clarification should this info move to total_income? Test data issue. In prod all values are "Not collected" not meaningful
    if 'personal_income_collect_method' in updated_record['data'].keys():
        if  updated_record['data']['personal_income_collect_method']=="Self-identified" or updated_record['data']['personal_income_collect_method']=="Derived":
            try:
                updated_record['data']['personal_income_collect_method']="Missing - Not applicable"
            except:
                error.append("Unable make %s into Missing - Not applicable' in record '%s'" % (col,record))                

    ### Test Data generation error 
    if  updated_record['data']['ethnicity']!="Another Ethnic or Cultural Origin":
        if "ethnicity_another_category" in updated_record['data'].keys():
            if updated_record['data']["ethnicity_another_category"]!=None:
                try:
                    del updated_record['data']["ethnicity_another_category"]
                except:
                    error.append("Unable to remove field %s to from record '%s'" % (col,record))

    ###Data migration as the enum was replaced.
    if 'education' in updated_record['data'].keys():
        if updated_record['data']['education']=="Bachelor's degree":
            try:
                updated_record['data']['education']='Undergraduate degree'
            except:
                error.append("Unable to update field %s from 'Bachelor's degree' to 'Undergraduate' record '%s'" % (col,record))


    ### Derive employment_status from employment_other free text
    ### 1. employment_other present -> mapped value
    ### 2. else status already an allowed value -> unchanged
    ### 3. else status reads unknown -> "Missing - Unknown"
    ### 4. else -> "Missing - Not provided"
    col='employment_status'
    employment_valid={
        "Employed full-time","Employed part-time",
        "Employed casual, on-call, temporary, or seasonal","Self-employed",
        "Parental leave of absence","Out of work or unemployed for 1 year or more",
        "Out of work or unemployed for less than 1 year","Looking after home and/or family",
        "A student","Retired",
        "Unable to work (for example, because of sickness or disability)",
        "Another status of employment","Prefer not to answer",
        "Missing - Not applicable","Missing - Unknown","Missing - Not collected",
        "Missing - Not provided","Missing - Restricted access",
    }
    # Order matters: first match wins
    employment_rules=[
        (r"^(0|na|non|none|n/a)$","Missing - Not applicable"),
        (r"^(her|widowed|senior \(81 year old\))$","Missing - Unknown"),
        (r"^employment_other$","Another status of employment"),
        (r"maternity leave|parental leave|mat leave","Parental leave of absence"),
        (r"home ?maker|house ?wife|stay[ -]at[ -]home|primary caretaker|^home$","Looking after home and/or family"),
        (r"(semi|partially)[ -]*(retire|retird)","Employed part-time"),
        (r"retire|retied|retird","Retired"),
        (r"disab|odsp|on canada pension plan|unable to work|illness|unwell|cancer|worker'?s comp|workers comp",
         "Unable to work (for example, because of sickness or disability)"),
        (r"\bstudent\b|undergrad|back to school|^school$|just graduate|\bph\.?d\b","A student"),
        (r"never worked|since 20[01][0-9]|many years|[0-9][0-9] years","Out of work or unemployed for 1 year or more"),
        (r"unemploy|laid off|not employed|not working|no job|no occupation|lost job|\bon ei\b",
         "Out of work or unemployed for less than 1 year"),
        (r"self[ -]*employ|freelance|entrepreneur|sole proprietor|own business|home based business|"
         r"contractor|private practice|day trading|independent|\b(owns?|owner|runs|founder|uber|gig)\b","Self-employed"),
        (r"part[ -]?time|lunch ?room supervisor","Employed part-time"),
        (r"casual|on[ -]call|seasonal|supply teacher|substitute|\b(temp|temporary)\b",
         "Employed casual, on-call, temporary, or seasonal"),
    ]
    try:
        other=updated_record['data'].get('employment_other')
        other=other.strip() if isinstance(other,str) else ""
        if other.startswith("Missing"):   # placeholder (e.g. migrated "Not applicable"), not free text
            other=""

        status=updated_record['data'].get(col)
        status=status.strip() if isinstance(status,str) else ""

        if other!="":
            new_status="Employed full-time"   # plain job title with no status information
            for pattern,label in employment_rules:
                if re.search(pattern,other.lower()):
                    new_status=label
                    break
            updated_record['data'][col]=new_status
        elif status in employment_valid:
            updated_record['data'][col]=status
        elif re.search(r"unknown|don.?t know|unsure",status,re.I):
            updated_record['data'][col]="Missing - Unknown"
        else:
            updated_record['data'][col]="Missing - Not provided"
    except Exception as e:
        error.append("Unable to update field '%s' from 'employment_other' in record '%s': %s" % (col,record,e))


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