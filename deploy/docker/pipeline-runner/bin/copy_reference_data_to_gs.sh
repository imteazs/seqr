#!/usr/bin/env bash

set -x -e

BUILD_VERSION=$1
GS_BUCKET=$2

gsuitl -m rsync -r /seqr-reference-data/GRCh${BUILD_VERSION} ${GS_BUCKET}/reference_data/GRCh${BUILD_VERSION}
gsutil cp /vep_configs/hail_dataproc/vep-GRCh${BUILD_VERSION}-loftee-gcloud.json ${GS_BUCKET}/reference_data/GRCh${BUILD_VERSION}