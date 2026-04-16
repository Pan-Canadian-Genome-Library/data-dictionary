#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
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
"""

import json
import copy
import pandas as pd
import requests
from io import BytesIO
import argparse

def main():
    """
    Simple script that sorts lectern schema according to googlespreadsheet
    """
    parser = argparse.ArgumentParser(description='Simple script to split dataframes')
    parser.add_argument('-k', '--key', dest="key", help="Google spreadsheet key", required=True,type=str)
    parser.add_argument('-g', '--gid', dest="gid", help="Google spreadsheet ID", required=True,type=str)
    parser.add_argument('-j', '--json', dest="json", help="PCGL Lectern Schema", required=True,type=str)
    parser.add_argument('-o', '--output_directory', dest="out_dir", help="Output directory to save divided records.", required=True,type=str) 

    cli_input= parser.parse_args()

    key=cli_input.key
    gid=cli_input.gid
    json_file=cli_input.json
    #key="1OsgXXvrb6jR_UApxlBeTiKFihdBAsNT_1WXHZ3N93bc"
    #gid="169771343"
    sheet_url="https://docs.google.com/spreadsheets/d/%s/export?format=csv&id=%s&gid=%s" % (key,key,gid)
    csv_export_url = sheet_url.replace('/editgid=', '/export?format=csv&gid=')
    #https://doc-10-3g-sheets.googleusercontent.com/export/ar8p0cg638ia3n06pke3c92670/8dir8qoe42ff1439t2lahclk0k/1730138410000/105250506097979753968/104625230692579285705/1lSB5nZ5u1T15qmB8T-w2Rovd0frG_x1d?format=csv&id=1lSB5nZ5u1T15qmB8T-w2Rovd0frG_x1d&gid=1991954103&dat=AAt6Q5UopMOSDcygVHn5ZOxJIm3X9iq34j0nTyxQoaQaLjEfX7C-ASMIUqb5tZym4UnXk1V-iLa9siJhV4ucy4Mdxn7jljQ4eHYSMTBoT8IVbnJKX31HMS69t7Hi4EvL0AaPRFm4T5fVisl5NUoBr3hRiX0DqYDzpQ6Yhm96mb2QmeYbN8CmuFlwLDpJArxD-W2p29inbrR5cgmky82wMhHS_h865UB7_B7BcZJITq4YUgl8tHnlazgmJEmQdrb62DhC45xAZQ7cnMbt1FM1SmVyXz08p_JvHyPgMe5hfG_5sbNWu9AJmG69WnVlaXRxHLZULyqNLV5Icmw6CmgpXd6EOqFR_cYiRjp1rJVbxxe9i5iAwfV1zSiVxs-5eDpHNrCBxzUpEldOGG70yHFtMAqL0ZQ2fEfVfOJSnaDIBaO6BP5dVwRh7eN6Lg5VulcxQ-aIE-xvYt3EvRBTiapsXG20jRcrIO77R2tBBiXEuvLktsskiA2Zf387vHzd2ee2yQWG3kGreJeSiFvDOyArwAhTXFezfoQ-wUeES-jzwhPrV3bJjnvV2z2ffzI3hFtDjElvLhQ-BiKgCHfN2RNsb0UKbtrsQKvCnZxfrUuJb4xK2v4FmOTcFP1Kzx1BU4CSPTZ6MGvWgSS_XBSiivnORfIaXEcoaqiycCOHhIvn6lJyDQJ4PPtH5FCkz0bGi7jNZ_I9jF51RW2lHH01GfHkPLssdNYzFWhrVtt9rRbd1nLpGqoEQ3yva4InZuk-O4CB0fz3jSfjzJ8Y_hlESKwdYfzUBQFoaPDQrQqdr8YxrmvngTctURvWta1AarGJSk78NulAvZeZs6klyYR2pwUb9h0URiciT9frcw-4zQEkY7OViO_5wSGJKuxl8M73-_l-_tcTGDgITk1OMoMpe8cL1iCvpvG1lU11kKW1siEyN_zNnLYWq7jrP7b8g7pAQHf3fpBorsHGIGLiIt47-JC4BzaaM8rE-m1N6ph4Rw
    r = requests.get(csv_export_url)
    data = r.content
    df=pd.read_csv(BytesIO(data))
    df['Entity']= [z.lower().replace(" ","_") for z in df['Entity'].values.tolist()]
    #print(df['Entity'].unique().tolist())

    with open(json_file) as json_data:
        original_schema = json.load(json_data)
        json_data.close()


    updated_schema=original_schema.copy()

    for index,schema in enumerate(updated_schema['schemas']):
        #print(index,schema['name'])
        updated_fields=[]
        #print(schema['name'],df.query("Entity=='%s'" % schema['name'])['Field'].values.tolist())
        for field_ordered in df.query("Entity=='%s'" % schema['name'])['Field'].values.tolist():
            #print(schema['name'],field_ordered)
            for field in schema['fields']:
                #print(schema['name'],"A",field_ordered,"B",field['name'])
                if field['name']==field_ordered:
                    updated_fields.append(field)
        #print(updated_fields)
        updated_schema['schemas'][index]['fields']=updated_fields


    with open("%s/sorted_%s" % (cli_input.out_dir,cli_input.json.split("/")[-1]), "w") as file:
        json.dump(updated_schema, file, indent=4, sort_keys=True)

if __name__ == "__main__":
    main()