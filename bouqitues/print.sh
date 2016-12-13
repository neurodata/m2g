#!/bin/bash

docker run --rm -v $PWD:/work -w /work boutiques/boutiques localExec.py -i ../inputs.json ./ndmg.json
