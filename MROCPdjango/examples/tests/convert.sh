#!/bin/bash

# convert.sh
# Created by Disa Mhembere on 2013-07-10.
# Email: disa@jhu.edu
# Copyright (c) 2013. All rights reserved.

DATA_DIR="/data/projects/disa/OCPprojects/testdata/graphInvariants/"

function convert ()
{
  TESTFILE_FN=$1
  TESTSCRIPT_FN=$2
  QUANTITY=$3
  RESULT_FN=$4

  for DRCTY in $(ls $DATA_DIR)
  do

    if [ $DRCTY = ClustCoeff ]; then INV=cc;
    elif [ $DRCTY = Degree ]; then INV=deg;
    elif [ $DRCTY = Eigenvl ]; then INV=eig;
    elif [ $DRCTY = Eigvect ]; then INV=eig;
    elif [ $DRCTY = LCC ]; then INV=lcc;
    elif [ $DRCTY = MAD ]; then INV=mad;
    elif [ $DRCTY = SS1 ]; then INV=ss1;
    elif [ $DRCTY = SVD ]; then INV=svd;
    elif [ $DRCTY = Triangle ]; then INV=tri;
    else
      echo "Unknown directory \"$DRCTY\" causing exit ... "
      echo "Unknown directory \"$DRCTY\" causing exit ... " >> $RESULT_FN
      exit 1 # error
    fi

    echo "Big $QUANTITY $DRCTY test ..."
    echo "Big $QUANTITY $DRCTY test ..." >> $RESULT_FN
    python $TESTSCRIPT_FN /data/projects/disa/OCPprojects/testdata/graphInvariants/$DRCTY/$TESTFILE_FN http://mrbrain.cs.jhu.edu/disa/convert/$INV/mat,csv,npy >> $RESULT_FN

  done
  printf "\n******************************************************\n"
}
# Delete old test results
if [ -f single_convert_result.meta ]
then
  rm -f single_convert_result
fi

if [ -f multi_convert_result.meta ]
then
  rm -f multi_convert_result.meta
fi

# run the directories
convert test.npy ../singleConvert.py single single_convert_result.meta
convert "" ../multiConvert.py multiple multi_convert_result.meta
