#!/bin/bash

# Change to the directory containing the .txt files
search_dir=/Users/thakrav/Documents/code/fire-and-blood-story-generation/data/processed-data/book-chapters/*.txt
output_dir=/Users/thakrav/Documents/code/fire-and-blood-story-generation/data/processed-data/logs
# Loop through all .txt files in the directory
for file in $search_dir
do
    # Call the Python script and pass the current file as an argument
    echo "$file"
    # extract the filename without the extension
    filename=$(basename "${file}" .txt)
    python -u context_extraction.py -cf $file | tee "${output_dir}/${filename}.txt"
done