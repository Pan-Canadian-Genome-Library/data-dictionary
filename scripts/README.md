### Generate custom linkML
```
python scripts/generateCustomLinkmlFromReference.py -c custom/example/example.yaml
```
### Convert linkML to Lectern
**Only accepts full linkML**
```
python scripts/generateLecternJsonFromCustomLinkml.py -c custom/example/example_full.yaml -r restrictions/example/restrictions.json
```
### Make DataHarmonizer index
```
cd DataHarmonizer/web/templates/example
python DataHarmonizer/script/linkml.py -i custom/example/example_dh.yaml
cd /Users/esu/Desktop/GitHub/DataHarmonizer
yarn dev
```