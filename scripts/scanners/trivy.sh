#!/bin/bash

TARGET_REPO="$1"
TOOLOUTPUT_FILE="$2"

cd "$TARGET_REPO"
trivy fs --scanners vuln,secret,misconfig -o "$TOOLOUTPUT_FILE" -f sarif .
