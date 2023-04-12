# A script to extract programs from .results.json files
import json
import argparse
from pathlib import Path
import gzip
import os
import itertools

def extract_programs(results, num_programs, output, lang):
    with gzip.open(results, "r") if os.path.splitext(results)[1] == ".gz" else open(results, "r") as f:
        result_json = json.load(f) 
        results = result_json["results"]

        for i in range(num_programs):
            with open(output / f"{i}-{results[i]['status']}.{lang}", "w") as f:
                f.write(results[i]["program"])

def main():

    args = argparse.ArgumentParser()

    args.add_argument("--input", help="The json file or directory of json files storing the evaluated completions.", type=Path, required=True)
    # list of programs to extract
    args.add_argument("--programs", help="The numbers of programs to extract from the results.", type=int, required=True)

    args.add_argument("--lang", help="The file extension to save the program as.", type=str, required=True)

    args.add_argument("--output-dir", type=Path, default="output/")

    args = args.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    if os.path.isdir(args.input):
        [extract_programs(p, args.programs, args.output_dir, args.lang) for p in itertools.chain(Path(args.input).glob("*.results.json"), Path(args.input).glob("*.results.json.gz"))]
    else:
        extract_programs(args.input, args.programs, args.output_dir, args.lang)

if __name__ == "__main__":
    main()