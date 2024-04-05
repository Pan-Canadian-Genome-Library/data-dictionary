$ python3 validate.py
All required columns present in study schema: True
All required columns present in participant schema: True
All required columns present in specimen schema: True
All required columns present in sample schema: True
All validations passed for study schema.
Error in participant schema: race has values not in codeList: ['white']
Error in participant schema: date_of_death has values not matching regex ^\d{4}\-(0?[1-9]|1[012])$: ['2009-13']
Error in specimen schema: specimen_anatomic_location has values not matching regex ^[C][0-9]{2}(.[0-9]{1})?$: ['C9']
Error in sample schema: sample_type has values not in codeList: ['Proteins']

error --> correct version
['white']   --> ['White'] 
['2009-13'] --> ['2009-01']
['C9']      --> ['C09']
['Proteins']--> ['Protein']