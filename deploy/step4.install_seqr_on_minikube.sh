#!/usr/bin/env bash

echo ==== Wait for minikube to start =====
set -x

for i in {1..150}; do    # timeout for 5 minutes
   kubectl get po &> /dev/null
   if [ $? -ne 1 ]; then
      break
  fi
  echo 'Waiting for minikube to start...'
  sleep 2
done

minikube status

set +x
echo ==== deploy all seqr components =====

source venv/bin/activate


#wget https://storage.googleapis.com/seqr-reference-data/gene_reference_data.gz
# --restore-seqrdb-from-backup gene_reference_data.gz 
./servctl deploy-all minikube