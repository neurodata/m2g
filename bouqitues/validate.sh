#!/bin/bash

docker run --rm -v $PWD:/work -w /work boutiques/boutiques validator.rb /usr/local/boutiques/schema/descriptor.schema.json ./ndmg.json
