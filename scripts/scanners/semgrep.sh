#!/bin/bash

TARGET_REPO="$1"
TOOLOUTPUT_FILE="$2"

cd "$TARGET_REPO"
semgrep scan -o "$TOOLOUTPUT_FILE" --sarif .
