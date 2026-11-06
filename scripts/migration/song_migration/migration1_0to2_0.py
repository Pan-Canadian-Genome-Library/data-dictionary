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

def experiment_submitter_id_to_submitter_ids(analysis):
    """
    Note the change was converting "submitter_experiment_id" to "submitter_experiment_ids".
    Originally the format was in string, so now have to convert to array of strings.
    """
    updated_record=analysis.copy()
    try:
        experiment=updated_record['submitter_experiment_id']
        del updated_record['submitter_experiment_id']
        updated_record['submitter_experiment_ids']=experiment.split("|")
        return(True,updated_record,None)
    except:   
        return(False,updated_record,"Unable to split 'submitter_experiment_id'")
    
def modify(records):
    """
    Generic function to be called by migrate.py. Iterate through analyses applying modifications
    Takes records[study][valid] and modifies contents into records[study][modified]
    """
    for study in records.keys():
        for analysis in records[study]["valid"]:
            modified,updated_record,reason=experiment_submitter_id_to_submitter_ids(analysis)

            if modified:
                records[study]['modified'].append(updated_record)
            else:
                records[study]['unmodified'][analysis['analysisId']]=reason

    return()