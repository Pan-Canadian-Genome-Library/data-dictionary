python scripts/generateCustomLinkmlFromReference.py -c custom/gen3g/gen3g.yaml -w $(pwd)
python scripts/generateLecternJsonFromCustomLinkml.py -c custom/gen3g/gen3g_full.yaml -r restrictions/pcgl/restrictions.json
###Validate Good data
linkml validate -C Participant -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Participant.yaml
linkml validate -C Sociodemographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Sociodemographic.yaml
linkml validate -C Phenotype -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Phenotype.yaml
linkml validate -C Comorbidity -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Comorbidity.yaml
linkml validate -C Measurement -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Measurement.yaml
linkml validate -C Exposure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Exposure.yaml
linkml validate -C Demographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Demographic.yaml
linkml validate -C Diagnosis -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Diagnosis.yaml
linkml validate -C Follow_Up -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Follow_up.yaml
linkml validate -C Treatment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Treatment.yaml
linkml validate -C Medication -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Medication.yaml
linkml validate -C Procedure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Procedure.yaml
linkml validate -C Radiation -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Radiation.yaml
linkml validate -C Specimen -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Specimen.yaml
linkml validate -C Sample -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Sample.yaml
linkml validate -C Experiment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Experiment.yaml
linkml validate -C Read_Group -s custom/pcgl/pcgl_full.yaml test_data/pcgl/good_data/Read_group.yaml

###Validate bad data
linkml validate -C Participant -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Participant.yaml
linkml validate -C Sociodemographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Sociodemographic.yaml
linkml validate -C Phenotype -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Phenotype.yaml
linkml validate -C Comorbidity -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Comorbidity.yaml
linkml validate -C Measurement -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Measurement.yaml
linkml validate -C Exposure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Exposure.yaml
linkml validate -C Demographic -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Demographic.yaml
linkml validate -C Diagnosis -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Diagnosis.yaml
linkml validate -C Follow_Up -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Follow_up.yaml
linkml validate -C Treatment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Treatment.yaml
linkml validate -C Medication -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Medication.yaml
linkml validate -C Procedure -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Procedure.yaml
linkml validate -C Radiation -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Radiation.yaml
linkml validate -C Specimen -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Specimen.yaml
linkml validate -C Sample -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Sample.yaml
linkml validate -C Experiment -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Experiment.yaml
linkml validate -C Read_Group -s custom/pcgl/pcgl_full.yaml test_data/pcgl/bad_data/Read_group.yaml
