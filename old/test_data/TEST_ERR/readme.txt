$ python3 ../script/validate.py
study: All required columns present -> True
study: All validations passed -> True

participant: All required columns present -> True
participant: Error -> row 3 race has values not in codeList: white
participant: Error -> row 3 date_of_death has values not matching regex ^\d{4}\-(0?[1-9]|1[012])$: 2009-13

specimen: All required columns present -> True
specimen: Error -> row 5 specimen_anatomic_location has values not matching regex ^[C][0-9]{2}(.[0-9]{1})?$: C9

sample: All required columns present -> True
sample: Error -> row 5 sample_type has values not in codeList: Proteins

error --> correct version
['white']   --> ['White'] 
['2009-13'] --> ['2009-01']
['C9']      --> ['C09']
['Proteins']--> ['Protein']