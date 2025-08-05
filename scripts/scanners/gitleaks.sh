#!/bin/bash

TARGET_REPO="$1"
TOOLOUTPUT_FILE="$2"

cd "$TARGET_REPO"
gitleaks detect -f sarif -r "$TOOLOUTPUT_FILE"
