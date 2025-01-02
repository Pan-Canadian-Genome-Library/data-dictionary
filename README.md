# Pan Canadian Genome Library Clinical Metadata Schema Repository
## About 
The repository serves as a resource for researchers and data coordination team to harmonize clinical metadata collection, utilizing existing ontologies and standards, provide an extensible interoperable framework for ease of data sharing.

### Schema Framework
The Schema framework is divided into three parts and defined as follows:
<table>
    <thead>
        <tr>
            <th>Term</th>
            <th>Definition</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td rowspan=3>Base</td>
            <td>Contains common data fields shared across all domains (e.g., patient demographics, vital status, laboratory results).</td>    
        </tr>
        <tr>
            <td>Defined and maintained by PCGL.</td>    
        </tr>
        <tr>
            <td>Drive the Research portal for data exploration to ensure all users interact with a consistent set of data elements and enhance the data interoperability</td>    
        </tr>
        <tr>
            <td rowspan=3>Extension</td>
            <td>Include domain-specific data fields unique to each study or disease area.</td>    
        </tr>
        <tr>
            <td>Collaboratively developed by individual Program/Study according to guidelines and templates provided by PCGL</td>    
        </tr>
        <tr>
            <td>Extend the base schema to meet the precise needs of each study without affecting the base schema</td>
        </tr>
        <tr>
            <td rowspan=4>Custom</td>
            <td>The result of merging the base schema and the extension schema.</td>    
        </tr>
        <tr>
            <td>Represents the complete schema used by a program or study.</td>    
        </tr>
        <tr>
            <td>Register to Lectern (Schema Registry)</td>
        </tr>
        <tr>
            <td>Stored, managed and versioned by Lectern</td>
        </tr>
    </tbody>
</table>

** INSERT Extensible schema DIAGRAM HERE **

### Schema Overview

Within Base, Extension and Custom are **Entities** that represent objects within the schema and serve as the basis for information collection. Types of entities include : participant, sample, treatment, etc...

Entities will contain fields which serve to collect a specific type of information for example a status, metric, a measurement or ID.

** INSERT ER DIAGRAM HERE **

### LinkML
The schemas are coded in linkML format. The following are reasons for utilizing linkML
- schemas can be used with DataHarmonizer, a browser spreadsheet editor locally and offline
- Data can validated through command line command locally and offline
- linkML supports object like inheritance
- Supports mapping for establish onotologies.

### Lectern and Lyric support
Both are overture products where lectern manages schemas while lyric manages data ingestion and validation.

Lectern utilizes a custom JSON formatted syntax that requires conversion from linkML format to Lectern accepted. We keep schemas in linkML format due to the previously mentioned strengths. For more details on downsides see `restrictions/README.md`.

## Repository Layout


|Folder|Purpose|
|--|--|
|Base| Contains YAML files of base entities|
|Extension| Sub-divided per project, contains YAML files that extend base entities|
|Custom| Sub-divided per project, contains 3 YAMLs. See README.md within folder for more details |
|Scripts| Scripts for aggregating schemas and exporting into various types.  See `README.md` within folder for more details |
|Lectern| Sub-divided per project,JSON schema files containing aggregated entities into a signle schema. See README.md within folder for more details |
|Restrictions| Sub-divided per project,JSON schema files containing specialized restrictions for entities. |
|Test_data| Sub-divided per project, contains examples of good and bad data for testing.|
|CSV| Sub-divided per project, contains the flattened CSV version of custom YAML|
|DataHarmonizer| Sub-divided per project, contains the zip packaged dataharmonizer for local offline validation.|
|Typescript_export| Sub-divided per project, contains the export typescript used for data harmonizer.|

## Data Coordination Center Admin Happy Path

Update to any of the following schema will require a full regeneration of resource:
- Base Schema (e.g. `base/participant.yaml`)
- Extension Schema (e.g. `extension/example/participant.yaml`)

1. Update Custom Schema (e.g. `extension/custom/participant.yaml`)
2. Use `scripts/generateCustomLinkmlFromReference.py` to generate `extension/custom/example_dh.yaml` and `extension/custom/example_full.yaml`

### Lectern resources

1. Use `scripts/generateFlatCsvFromFullLinkml.py` and `extension/custom/example_full.yaml` to generate `csv/example/example.yaml`
2. Use `scripts/generateLecternJsonFromCustomLinkml` and `extension/custom/example_full.yaml` to generate `lectern/example/example.json`
3. Register `lectern/example/example.json` in lectern per project
4. Register Lectern provided IDs in Lyric

### Dataharmonizer resources

1. Pull latest version of https://github.com/cidgoh/DataHarmonizer locally
2. Run `scripts/dh-validate.py` from `DataHarmonizer` folder on `extension/custom/example_dh.yaml` to generate `web/templates/examples/schema.json`
3. Copy `typescript_export/example/export.js` to `web/templates/examples`
4. Compress folder and copy over to `dataHarmonizer/example/example.tar.gz`
