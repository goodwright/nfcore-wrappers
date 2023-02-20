#!/bin/bash

# Path to the text file containing the list of parameters
PARAMS_FILE="./assets/module_list.txt"

# Loop through each line in the text file
while read -r PARAM; do
    # Run the Python script with the current parameter
    ./bin/create_wrapper.py --target "$PARAM"
done < "$PARAMS_FILE"
