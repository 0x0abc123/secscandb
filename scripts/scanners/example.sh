#!/bin/bash

TARGET_REPO="$1"
TOOLOUTPUT_FILE="$2"

cd "$TARGET_REPO"
echo "this is an example of a static analysis tool script"
echo "it should take two arguments: <path_to_repo_to_scan> <output_file>"
echo "SARIF format (JSON) output from the tool should be saved to the output file path"
echo "if anything goes wrong, the output file should be empty"
echo "simulating scan:"
echo examplescantool dir . -f sarif -o "$TOOLOUTPUT_FILE"
