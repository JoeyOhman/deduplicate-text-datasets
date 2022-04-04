#!/bin/bash

DATASET_DIR=data
# DATASET_DIR=data_not_used
DATA_OUT_DIR=data_out
DATASET_NAME=json
DO_TOKENIZE=""
# Tokenize does not seem to give any duplication hits for dummy data? Does it work?
# DO_TOKENIZE="--tokenize"

LEN_THRESHOLD=15  # paper uses 50 (or 100 for tokenized)
NUM_THREADS=8

TMP_CACHE_DIR=/tmp/cache

mkdir -p tmp
mkdir -p /tmp/cache

rm $DATA_OUT_DIR/*
rm $TMP_CACHE_DIR/*
rm tmp/*

### DO STUFF ###

# Load jsonl dataset file, TODO: check if it works for multiple files
python3 scripts/load_dataset_hf.py --data_dir $DATASET_DIR --save_dir $DATA_OUT_DIR --name $DATASET_NAME \
          --split train $DO_TOKENIZE --text_feature_key text

# This is to avoid the error: "too many open files"
ulimit -Sn 1000000

# Create the suffix array, this takes the majority of the time
python3 scripts/make_suffix_array.py $DATA_OUT_DIR/${DATASET_NAME}.train $DO_TOKENIZE

# Count occurrences of a particular string, for fun
python3 scripts/count_occurrences.py --suffix $DATA_OUT_DIR/${DATASET_NAME}.train --query dummy $DO_TOKENIZE

# Find number of duplicates
cargo run self-similar --data-file $DATA_OUT_DIR/${DATASET_NAME}.train --length-threshold $LEN_THRESHOLD \
        --cache-dir $TMP_CACHE_DIR --num-threads $NUM_THREADS

# Collect duplicates
cargo run collect --data-file $DATA_OUT_DIR/${DATASET_NAME}.train --cache-dir $TMP_CACHE_DIR \
        --length-threshold $LEN_THRESHOLD > $DATA_OUT_DIR/${DATASET_NAME}.train.remove

# exit
# $TMP_CACHE_DIR/${DATASET_NAME}.train.remove.byterange

python3 scripts/finish_single_file_new.py $DATA_OUT_DIR/${DATASET_NAME}.train \
          $DATA_OUT_DIR/${DATASET_NAME}.train.remove \
          $DATA_OUT_DIR/${DATASET_NAME}.train.dedup.jsonl
