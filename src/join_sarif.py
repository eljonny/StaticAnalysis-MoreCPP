import argparse
import json
import jsonpickle

from sarif_om import SarifLog

def join_sarif(files):
    joined = None
    for file in files:
        with open(file) as sarif_file:
            sarif_json = json.load(sarif_file)
            
            schema_key = "$schema"
            del sarif_json[schema_key]

            if joined == None:
                joined = SarifLog(**sarif_json)
                continue
            
            to_join = SarifLog(**sarif_json)
            for run in to_join.runs:
                joined.runs.append(run)
    
    return joined

def write_joined_sarif(joined_sarif, output_file):
    with open(output_file, "w") as out:
        out.write(jsonpickle.encode(joined_sarif))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--files",
        help="Space-separated list of SARIF files to join.",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Aggregate the SARIF results to this output file.",
        required=True,
    )

    files_to_join = str(parser.parse_args().files).split(" ")
    joined_sarif = join_sarif(files_to_join)

    output_file = parser.parse_args().output
    write_joined_sarif(joined_sarif, output_file)
