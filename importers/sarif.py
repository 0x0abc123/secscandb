import json
import time
import sys
import urllib.request
import urllib.error

def import_sarif(fileToImport, repoName, apiUrl):

    def titleGeneratorGitleaks(rule_obj):
        return rule_obj['id']

    def titleGeneratorSemgrep(rule_obj):
        return rule_obj['id'].split('.')[-1]

    def titleGeneratorDefault(rule_obj):
        title = ''
        if 'shortDescription' in rule_obj:
            title = rule_obj['shortDescription']['text']
        elif 'messageStrings' in rule_obj and 'default' in rule_obj['messageStrings']:
            title = rule_obj['messageStrings']['default']['text']
        return title

    titleGenerators = {
        'gitleaks':titleGeneratorGitleaks,
        'semgrep':titleGeneratorSemgrep,
        'default':titleGeneratorDefault,
    }

    def detailsGeneratorGitleaks(result_obj, rulesLookup):
        return detailsGeneratorDefault(result_obj, rulesLookup)

    def detailsGeneratorSemgrep(result_obj, rulesLookup):
        return detailsGeneratorDefault(result_obj, rulesLookup)

    def detailsGeneratorDefault(result_obj, rulesLookup):
        text = ''
        try:
            text = result_obj['ruleId']
            text = text + "\n" + result_obj['message']['text']
            snip = result_obj['locations'][0]['physicalLocation']['region']['snippet']['text']
            if len(snip) > 1000:
                snip = snip[:1000]
            text = text + "\nSnippet:\n" + snip
        except:
            pass
        return text

    detailsGenerators = {
        'gitleaks':detailsGeneratorGitleaks,
        'semgrep':detailsGeneratorSemgrep,
        'default':detailsGeneratorDefault,
    }

    file_content = ''

    try:
        with open(fileToImport, 'r') as file:
            file_content = file.read()
    except FileNotFoundError:
        print(f"Error: The file '{fileToImport}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    sarifObj = json.loads(file_content)

    runs = []

    timestamp_seconds = time.time()

    for run in sarifObj['runs']:

        rulesLookupTitle = {}
        rulesLookupSeverity = {}
        rulesLookup = {}

        toolName = run['tool']['driver']['name'].split(' ')[0].lower()

        rulesPresent = 'rules' in run['tool']['driver']

        if rulesPresent:
            for rule in run['tool']['driver']['rules']:
                rulesLookup[rule['id']] = rule
                rulesLookupTitle[rule['id']] = titleGenerators[toolName](rule) if toolName in titleGenerators else titleGenerators['default'](rule)

                # levels: error, warning, note, none
                if 'defaultConfiguration' in rule and 'level' in rule['defaultConfiguration']:
                    rulesLookupSeverity[rule['id']] = rule['defaultConfiguration']['level']


        if 'results' in run:
            for result in run['results']:
                title = ''
                severity = ''
                location = ''
                details = ''

                #title
                ruleID = result['ruleId']
                if ruleID in rulesLookupTitle:
                    title = rulesLookupTitle[ruleID]
                else:
                    title = result['message']['text']
                #severity
                if 'level' in result:
                    severity = result['level']
                elif ruleID in rulesLookupSeverity:
                    severity = rulesLookupSeverity[ruleID]
                else:
                    severity = 'note'
                #location
                if 'locations' in result:
                    loc_file = ''
                    loc_line = ''
                    if len(result['locations']) > 0:
                        if 'physicalLocation' in result['locations'][0]:
                            if 'artifactLocation' in result['locations'][0]['physicalLocation']:
                                if 'uri' in result['locations'][0]['physicalLocation']['artifactLocation']:
                                    loc_file = result['locations'][0]['physicalLocation']['artifactLocation']['uri']
                            if 'region' in result['locations'][0]['physicalLocation']:
                                if 'startLine' in result['locations'][0]['physicalLocation']['region']:
                                    loc_line = result['locations'][0]['physicalLocation']['region']['startLine']
                        location = f'{loc_file}:{loc_line}'

                details = detailsGenerators[toolName](result, rulesLookup) if toolName in detailsGenerators else detailsGenerators['default'](result, rulesLookup)

                json_data = {
                    "project": repoName,
                    "object": {
                        "title": title,
                        "loc": location,
                        "severity": severity,
                        "details": details,
                        "timestamp": timestamp_seconds,
                        "tool": toolName
                    }
                }

                # Create the request with headers
                req = urllib.request.Request(
                    apiUrl,
                    data=json.dumps(json_data).encode("utf-8"),
                    headers={
                        "Content-Type": "application/json"
                    },
                    method="POST"
                )

                # Send the request and read the response
                try:
                    with urllib.request.urlopen(req) as response:
                        result = response.read().decode("utf-8")
                        print("Response:", result)
                except urllib.error.HTTPError as e:
                    print("HTTP Error:", e.code, e.read().decode("utf-8"))
                except urllib.error.URLError as e:
                    print("URL Error:", e.reason)


USAGE = """
Takes 3 positional arguments:
<sarif-input-file> <repoName> <url-of-api>

example:
python3 sarif.py /path/to/tooloutput.sarif my_repo_name http://localhost:8000/upsert_data
"""
if len(sys.argv) < 4:
    print(USAGE)
    exit(1)

import_sarif(sys.argv[1], sys.argv[2], sys.argv[3])
