### Generate custom linkML
```
python scripts/generateCustomLinkmlFromReference.py -c custom/example/example.yaml -w $(pwd)
```
### Convert linkML to Lectern
**Only accepts full linkML**
#### With restrictions
```
python scripts/generateLecternJsonFromCustomLinkml.py -c custom/example/example_full.yaml -r restrictions/example/restrictions.json
```
#### Without restrictions
```
python scripts/generateLecternJsonFromCustomLinkml.py -c custom/example/example_full.yaml
```
### Make DataHarmonizer index
```
cd DataHarmonizer/web/templates/example
python DataHarmonizer/script/linkml.py -i custom/example/example_dh.yaml
cd /Users/esu/Desktop/GitHub/DataHarmonizer
yarn dev
###Navigate to default http://localhost:8080/
```
### Generate data dictionary package
```
python scripts/generateDataHarmonizerPackage.py -o $(pwd) -s $HOME/Desktop/GitHub/pcgl/data-dictionary
```
### Flatten model for definitions
```
python scripts/generateFlatDefinitionsTsvFromFullLinkml.py -c custom/example/example_full.yaml -o csv/definition/example
```
### Generate template TSVs
```
python scripts/generateTemplateTsvFromFullLinkml.py -c custom/pcgl/pcgl_full.yaml -o csv/template/pcgl
```
### Data validation
```
linkml validate -C Comorbidity -s custom/example/example_full.yaml test_data/example/good_data/comorbidity.tsv
linkml validate -C Demographic -s custom/example/example_full.yaml test_data/example/good_data/demographic.tsv
linkml validate -C Diagnosis -s custom/example/example_full.yaml test_data/example/good_data/diagnosis.tsv
linkml validate -C Exposure -s custom/example/example_full.yaml test_data/example/good_data/exposure.tsv
linkml validate -C Follow_up -s custom/example/example_full.yaml test_data/example/good_data/follow_up.tsv
linkml validate -C Imaging -s custom/example/example_full.yaml test_data/example/good_data/imaging.tsv
linkml validate -C Measurement -s custom/example/example_full.yaml test_data/example/good_data/measurement.tsv
linkml validate -C Medication -s custom/example/example_full.yaml test_data/example/good_data/medication.tsv
linkml validate -C Participant -s custom/example/example_full.yaml test_data/example/good_data/participant.tsv
linkml validate -C Phenotype -s custom/example/example_full.yaml test_data/example/good_data/phenotype.tsv
linkml validate -C Procedure -s custom/example/example_full.yaml test_data/example/good_data/procedure.tsv
linkml validate -C Specimen -s custom/example/example_full.yaml test_data/example/good_data/specimen.tsv
linkml validate -C Treatment -s custom/example/example_full.yaml test_data/example/good_data/treatment.tsv

linkml validate -C Comorbidity -s custom/example/example_full.yaml test_data/example/bad_data/comorbidity.yaml
linkml validate -C Demographic -s custom/example/example_full.yaml test_data/example/bad_data/demographic.yaml
linkml validate -C Diagnosis -s custom/example/example_full.yaml test_data/example/bad_data/diagnosis.yaml
linkml validate -C Exposure -s custom/example/example_full.yaml test_data/example/bad_data/exposure.yaml
linkml validate -C Follow_up -s custom/example/example_full.yaml test_data/example/bad_data/follow_up.yaml
linkml validate -C Imaging -s custom/example/example_full.yaml test_data/example/bad_data/imaging.yaml
linkml validate -C Measurement -s custom/example/example_full.yaml test_data/example/bad_data/measurement.yaml
linkml validate -C Medication -s custom/example/example_full.yaml test_data/example/bad_data/medication.yaml
linkml validate -C Participant -s custom/example/example_full.yaml test_data/example/bad_data/participant.yaml
linkml validate -C Phenotype -s custom/example/example_full.yaml test_data/example/bad_data/phenotype.yaml
linkml validate -C Procedure -s custom/example/example_full.yaml test_data/example/bad_data/procedure.yaml
linkml validate -C Specimen -s custom/example/example_full.yaml test_data/example/bad_data/specimen.yaml
linkml validate -C Treatment -s custom/example/example_full.yaml test_data/example/bad_data/treatment.yaml
```

### Generate Molecular Metadata Schemas and Templates
#### Prerequisites
Before running `scripts/gen_song_schema.py`, ensure you have the following:
1. Python Environment

- Python 3.7 or higher is recommended.
- (Optional but recommended) Use a virtual environment:

2. Required Python Packages
```
pip install jsonref jsonschema
```  

3. LinkML Toolkit

The script uses the linkml CLI tool to generate JSON schemas. Install it via pip:
```
pip install linkml
```

4. Input Files
- A LinkML YAML schema file (e.g., pcgl_song_schema.yaml).
- A configuration JSON file specifying top classes and options (e.g., options.json).

#### Command Line Usage
```
python3 scripts/gen_song_schema.py \
--input_file song_schema/linkml/pcgl_song_schema.yaml \
--config_file song_schema/conf/options.json \
--output_schema_dir song_schema/json-schema
```