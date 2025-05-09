python scripts/generateCustomLinkmlFromReference.py -c custom/pcgl/pcgl.yaml -w $(pwd)
python scripts/generateLecternJsonFromCustomLinkml.py -c custom/pcgl/pcgl_full.yaml -r restrictions/pcgl/restrictions.json
###Validate Good data
linkml validate -C Participant -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Participant.tsv
linkml validate -C Sociodemographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Sociodemographic.tsv
linkml validate -C Phenotype -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Phenotype.tsv
linkml validate -C Comorbidity -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Comorbidity.tsv
linkml validate -C Measurement -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Measurement.tsv
linkml validate -C Exposure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Exposure.tsv
linkml validate -C Demographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Demographic.tsv
linkml validate -C Diagnosis -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Diagnosis.tsv
linkml validate -C Follow_Up -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Follow_up.tsv
linkml validate -C Treatment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Treatment.tsv
linkml validate -C Medication -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Medication.tsv
linkml validate -C Procedure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Procedure.tsv
linkml validate -C Radiation -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Radiation.tsv
linkml validate -C Specimen -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Specimen.tsv
linkml validate -C Sample -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Sample.tsv
linkml validate -C Experiment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Experiment.tsv
linkml validate -C Read_Group -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Read_group.tsv

###Validate bad data
linkml validate -C Participant -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Participant.tsv
linkml validate -C Sociodemographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Sociodemographic.tsv
linkml validate -C Phenotype -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Phenotype.tsv
linkml validate -C Comorbidity -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Comorbidity.tsv
linkml validate -C Measurement -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Measurement.tsv
linkml validate -C Exposure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Exposure.tsv
linkml validate -C Demographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Demographic.tsv
linkml validate -C Diagnosis -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Diagnosis.tsv
linkml validate -C Follow_Up -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Follow_up.tsv
linkml validate -C Treatment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Treatment.tsv
linkml validate -C Medication -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Medication.tsv
linkml validate -C Procedure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Procedure.tsv
linkml validate -C Radiation -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Radiation.tsv
linkml validate -C Specimen -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Specimen.tsv
linkml validate -C Sample -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Sample.tsv
linkml validate -C Experiment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Experiment.tsv
linkml validate -C Read_Group -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Read_group.tsv
