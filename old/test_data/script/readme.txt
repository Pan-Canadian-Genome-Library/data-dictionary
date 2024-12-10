# option 1: validate all tsv files under a directory
python3 validate.py ../TEST_ERR

python3 validate.py ../TEST_PRO

# option 2: validate a single tsv file
python3 validate.py ../TEST_ERR/sample_test.tsv

python3 validate.py ../TEST_PRO/participant_test.tsv

# option 3: validate four tsv files (default: study_test.tsv, participant_test.tsv, specimen_test.tsv, sample_test.tsv) under current directory
cd ../TEST_ERR
python3 ../script/validate.py

cd ../TEST_PRO
python3 ../script/validate.py