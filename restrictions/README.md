# About
Throwing this here to document discussions b/c at the moment there is no method to fully validate our data across all criteria

## Translating restrictions in LinkML to Lectern
Key issue here in linkML restriction is defined in the class/entity while for lectern its defined in the slot/field

For complex cases, this becomes significantly harder to navigate.

As such as a temporary measure, restrictions are translated by hand from linkML to lectern and referenced when using `generateLecternJsonFromCustomLinkml.py`

### Understanding differences in syntax
To start off example in Lectern, restrictions are described as such:
```
{
	"name": "example_field",
	"description": "Shows a string field with a required restriction",
	"meta": { /* Custom meta data abou the field here */ },
	"isArray": false,

	"valueType": "string",
	"restrictions": {
        "if": {
            "conditions": [ /* Restriction conditions */ ],
            "case": "all"
        },
        "then": {/* Restrictons */} OR [ /* Restrictions objects (restriction values or nested conditional restrictions */ ],
        "else": {/* Restrictons */} OR [ /* Restrictions objects (restriction values or nested conditional restrictions */ ]
    }
}
```
For linkML:
```
classes:
  Address:
    slots:
      - street_address
      - country
    rules:
      - preconditions:
          slot_conditions:
            country:
              any_of:
                - equals_string: USA
                - equals_string: USA_territory
        postconditions:
          slot_conditions:
            postal_code:
              pattern: "[0-9]{5}(-[0-9]{4})?"
            telephone:
              pattern: "^\\+1 "
        description: USA and territories must have a specific regex pattern for postal codes and phone numbers
```
### Implementing conditional column
For example we only want to populat either fieldA or fieldB
For linkML, we can set one `if` to affect multiple fields:
```
- preconditions:
    description: An example of if fieldA is missing provide fieldA_null_reason. Common in virus-seq
    slot_conditions:
        image_processing_personel:
            value_presence: ABSENT
    postconditions:
        slot_conditions:
            image_processing_null_reason:
                any_of:
                    - range: ImageProcessingNullReasonMenu
            image_processing_personel:
                required: false
                value_presence: ABSENT
    elseconditions:
        slot_conditions:
            image_processing_personel:
                range: string
                required: true
            image_processing_null_reason:
                value_presence: ABSENT
```
For lectern, b/c restrictions are at field level. To emulate this, we'd have to have a conditional check per affected field.
```
[
    {
        "name": "image_processing_personel",
        "restrictions": {
        "if": {
            "conditions": [
            {
                "field": "Image Processing Null Reason",
                "exists": false
            }
            ],
            "case": "all"
        },
        "then": {
            "required": true,
            "valueType": "string"
        }
        }
    },
    {
        "name": "image_processing_null_reason",
        "restrictions": {
        "if": {
            "conditions": [
            {
                "field": "Image Processing Personel",
                "exists": false
            }
            ],
            "case": "all"
        },
        "then": {
            "required": true,
            "codeList": [
            "Unknown",
            "Not Provided",
            "Revoked"
            ]
        },
        "else": {
            "empty": true
        }
        }
    }
]
```
### Implementing conditional enum based on another column
For example we want to populate `fieldB` with a subset of enums according to the value of `fieldA`
linkML - we require multiple `IF`s statements :
```
- preconditions:
    description: 'An example of if value==''A'' must follow enum

        1/3 conditions'
    slot_conditions:
        image_hosted_format:
            equals_string: "PNG"
    postconditions:
        slot_conditions:
            image_processing_pipeline:
                any_of:
                    - range: ImageProcessPngPipelineMenu
- preconditions:
    description: 'An example of if value==''A'' must follow enum

        1/3 conditions'
    slot_conditions:
        image_hosted_format:
            equals_string: "SVG"
    postconditions:
        slot_conditions:
            image_processing_pipeline:
                any_of:
                    - range: ImageProcessSvgPipelineMenu
- preconditions:
    description: "An example of if value=='A' must follow enum\n1/3 conditions"
    slot_conditions:
        image_hosted_format:
            any_of:
                - equals_string: "PDF"
                - equals_string: "JPEG"
    postconditions:
        slot_conditions:
            image_processing_pipeline:
                any_of:
                    - range: ImageProcessPdfJpegPipelineMenu
```
For Lectern, restrictions can only have one `IF` statement. Even though it can accept multiple conditions, we cannot dictate conditionA triggers outcome. As such we rely if else nested structure:
```
"restrictions": {
            "if": {
              "conditions": [
                {
                  "field": "image_hosted_format",
                  "match": {
                    "value": "PNG"
                  }
                }
              ],
              "case": "all"
            },
            "then": {
              "required": true,
              "valueType": "string",
              "codeList": [
                "pipelineA",
                "pipelineB",
                "pipelineC"
              ]
            },
            "else": {
              "if": {
                "conditions": [
                  {
                    "field": "image_hosted_format",
                    "match": {
                      "value": "SVG"
                    }
                  }
                ],
                "case": "all"
              },
              "then": {
                "required": true,
                "valueType": "string",
                "codeList": [
                  "pipelineA",
                  "pipelineD",
                  "pipelineE"
                ]
              },
              "else": {
                "if": {
                  "conditions": [
                    {
                      "field": "image_hosted_format",
                      "match": {
                        "value": "JPEG"
                      }
                    }
                  ],
                  "case": "any"
                },
                "then": {
                  "required": true,
                  "valueType": "string",
                  "codeList": [
                    "pipelineA",
                    "pipelineD",
                    "pipelineF"
                  ]
                },
                "else": {}
              }
            }
}
```
## Criteria checking across methods
|Criteria|linkML command Line| DataHarmonizer | Lectern | Notes|
|--|--|--|--|--|
|Unique ID check | Currently not possible | Possible within spreadsheet but not against existing IDs| Working | https://github.com/linkml/linkml/issues/1542|
|Conditional Enum (e.g. if `fieldX` is `A` fieldY can only be `5,6,7` else `1,2,3`)| Working | Does not work | Under implementation |  https://github.com/cidgoh/DataHarmonizer/issues/302 |
