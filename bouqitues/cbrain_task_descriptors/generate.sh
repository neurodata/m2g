#!/bin/bash

if [ $# -eq 0 ]
  then
    num=5
else
    num=$1
fi

docker run --rm -v $PWD:/work -w /work boutiques/boutiques localExec.py -n ${num} -r ./ndmg.json
