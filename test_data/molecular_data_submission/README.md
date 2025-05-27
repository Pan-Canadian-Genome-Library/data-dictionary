  1. Start the file-manager-client docker container
token=NNNN-NNNN-NNNNN
studyId=YOUR_STUDY_HERE
docker run -d -it \
--name pcgl-file-manager \
-e CLIENT_ACCESS_TOKEN=${token} \
-e CLIENT_STUDY_ID=${studyId} \
-e CLIENT_SERVER_URL=https://file-manager.pcgl-dev.cumulus.genomeinformatics.org \
--mount type=bind,source="$(pwd)",target=/output \
ghcr.io/pan-canadian-genome-library/file-manager-client:edge

  2. Start the file-transfer docker container
token=NNNN-NNNN-NNNNN
docker run -d -it \
--name pcgl-file-transfer \
-e ACCESSTOKEN=${token} \
-e STORAGE_URL=https://file-transfer.pcgl-dev.cumulus.genomeinformatics.org \
-e METADATA_URL=https://file-manager.pcgl-dev.cumulus.genomeinformatics.org \
--mount type=bind,source="$(pwd)",target=/output \
ghcr.io/pan-canadian-genome-library/file-transfer:edge

  3. Song submit
docker exec pcgl-file-manager sh -c "sing submit -f /output/fastq/sequenceExperimentPayload.json"

  4. Song generate manifest file
docker exec pcgl-file-manager sh -c "sing manifest -a a4142a01-1274-45b4-942a-01127465b422 -f /output/fastq/manifest.txt -d /output/fastq/files"
  
  5. Upload files
docker exec pcgl-file-transfer sh -c "score-client upload --manifest output/fastq/manifest.txt"
  
  6. Publish Analysis
docker exec pcgl-file-manager sh -c "sing publish -a a4142a01-1274-45b4-942a-01127465b422"

