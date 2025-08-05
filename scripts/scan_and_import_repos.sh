#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# check config
if [[ ! -f config.env ]]
then
  echo "ensure config.env is present in $SCRIPT_DIR"
  echo "exiting..."
  exit 1
fi

source ./config.env

logger() {
  echo "[$(date +%s)] -" "$1" | tee -a $LOG_FILE
}

# check installed gh
if ! command -v gh >/dev/null 2>&1; then
  logger "github CLI (gh) is not installed or in PATH, exiting."
  exit 1
fi

# check install jq
if ! command -v jq >/dev/null 2>&1; then
  logger "jq is not installed or in PATH, exiting."
  exit 1
fi

# check install python3
if ! command -v python3 >/dev/null 2>&1; then
  logger "python3 is not installed or in PATH, exiting."
  exit 1
fi

# check install curl
if ! command -v curl >/dev/null 2>&1; then
  logger "curl is not installed or in PATH, exiting."
  exit 1
fi

# check running secscandb
if ! curl -s "$SECSCANDB_URL" >/dev/null 2>&1; then
  logger "The secscandb instance at $SECSCANDB_URL could not be reached"
  exit 1
fi


export GH_PROMPT_DISABLED=1

gh auth login -p

if [[ ! -d $LOCAL_REPOS_DIR ]] ; then mkdir -p $LOCAL_REPOS_DIR ; fi
cd $LOCAL_REPOS_DIR

if [[ -f repos.txt ]]
then

    for REPO_URL in `cat repos.txt`
    do
        cd $LOCAL_REPOS_DIR
        REPO=$(echo $REPO_URL | cut -d / -f5 )
        if [[ ! -d "$REPO" ]]
        then
            logger "cloning $REPO under parent $(pwd)"
            gh repo clone $(echo $REPO_URL | cut -d / -f4- )
        else
            cd $REPO
            logger "syncing $REPO"
            gh repo sync
        fi

        SCANNERS_DIR="$SCRIPT_DIR/scanners"
        for TOOL_SCRIPT in `ls -1 $SCANNERS_DIR`
        do
            TMP_OUTPUT=$(mktemp --suffix=.sarif)
            sh "$SCANNERS_DIR/$TOOL_SCRIPT" "$LOCAL_REPOS_DIR/$REPO" "$TMP_OUTPUT"
            if [[ ! $(jq .runs[0].results[0] $TMP_OUTPUT) == "" ]]
            then
                python3 "$SCRIPT_DIR/$SARIF_IMPORTER" "$TMP_OUTPUT" "$REPO" "$SECSCANDB_URL"
            else
                logger "no output from $SCANNERS_DIR/$TOOL_SCRIPT for $REPO"
            fi
            rm $TMP_OUTPUT
        done
    done
else
    logger "repos.txt was not found, so it will be created with all accessible repos as its contents"
    gh repo list $GH_ORG --json url --jq '.[].url' > repos.txt
    logger "$(wc -l repos.txt) repos were found and added to $(pwd)/repos.txt"
    echo "these were the repos you have access to:"
    cat repos.txt
    echo "you should check the list of repo URLs and add/remove any you need to before running the script again."
fi
