import json

from sarif_om import SarifLog

def to_list_and_sort(string_in):
    # create list (of strings) from space separated string
    # and then sort it
    list_out = string_in.split(" ")
    list_out.sort()

    return list_out

def generate_comment(comment_title, content, issues_found, tool_name):
    SEPARATOR = "\n\n\n *** \n"

    if issues_found == 0:
        return (
            '## <p align="center"><b> :white_check_mark:'
            f"{comment_title} - no issues found! :white_check_mark: </b></p>"
        )

    expected_comment_body = (
        f'## <p align="center"><b> :zap: {comment_title} :zap: </b></p> \n\n'
    )

    if tool_name == "cppcheck":
        expected_comment_body += SEPARATOR
    elif tool_name == "fbinfer":
        expected_comment_body += SEPARATOR + SEPARATOR
    elif tool_name == "clang-tidy":
        expected_comment_body += SEPARATOR + SEPARATOR + SEPARATOR

    expected_comment_body += (
        f"<details> <summary> <b> :red_circle: {tool_name} found "
        f"{issues_found} {'issues' if issues_found > 1 else 'issue'}!"
        " Click here to see details. </b> </summary> <br>"
        f"{content} </details>"
    )

    if tool_name == "flawfinder":
        expected_comment_body += SEPARATOR + SEPARATOR + SEPARATOR
    elif tool_name == "cppcheck":
        expected_comment_body += SEPARATOR + SEPARATOR
    elif tool_name == "fbinfer":
        expected_comment_body += SEPARATOR
    else:
        expected_comment_body += "<br>\n"

    return expected_comment_body

def genhashes(to_join):
    hashes = []

    for sarif_run in to_join:
        with open(sarif_run) as file:
            sarif_json = json.load(file)

            schema_key = "$schema"
            del sarif_json[schema_key]

            sarif = SarifLog(**sarif_json)
            for run in sarif.runs:
                hashes.append(hash(json.dumps(run, sort_keys=True, ensure_ascii=True, default=lambda v: repr(v) + str(hash(v)))))

    return hashes
