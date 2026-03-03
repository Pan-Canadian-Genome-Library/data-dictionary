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

import pandas as pd
import os
import argparse

def main():
	"""
	Simple script that takes a TSV/CSV file and spltis according to size. Subsetted files are saved into enumerated folders named after the input TSV. 
	"""
	parser = argparse.ArgumentParser(description='Simple script to split dataframes')
	parser.add_argument('-i', '--input', dest="input", help="The custom schema that makes references to extension and base schemas", required=True,type=str)
	parser.add_argument('-s', '--size', dest="size", help="The main directory containing folders : Base, Extension, Custom", default=True,type=str) 
	parser.add_argument('-o', '--output_directory', dest="out_dir", help="The main directory containing folders : Base, Extension, Custom", default=True,type=str) 

	cli_input= parser.parse_args()

	input_file = cli_input.input
	output_root = cli_input.out_dir
	chunk_size = cli_input.size

	chunk_iter = pd.read_csv(input_file, chunksize=chunk_size)

	for i, chunk in enumerate(chunk_iter, start=1):
		base_file=input_file.split("/")[-1].replace(".csv","").replace(".tsv","")
		output_dir="%s/%s_%s" % (output_root,base_file,str(i))
		os.makedirs(output_dir, exist_ok=True)
		output_file = "%s/%s.csv" % (output_dir,base_file)
	    
		chunk.to_csv(
		output_file,
		index=False,
		sep=",",
		encoding="utf-8-sig"  # UTF-8 with BOM
		)

		print(output_dir,output_file)

	print("Splitting complete.")

if __name__ == "__main__":
    main()