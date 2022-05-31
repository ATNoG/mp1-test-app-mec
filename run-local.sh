#!/bin/sh

set -eu

cd docker-img-application
./build.sh
cd -

docker run --rm -ti \
	--network="host" \
        -e MEC_BASE="http://0.0.0.0:8080" \
        -e APP_INSTANCE_ID="997fc80a-cfc1-498a-b77f-608f09506e86" \
	mep-test:latest
