import gzip
from pathlib import Path
from argparse import ArgumentParser
from multipl_e.util import gunzip_json
import json

def main():
    args = ArgumentParser()
    args.add_argument("--dir", help="Directory to change all the tabs to 4 spaces", required=True, type=Path)
    args = args.parse_args()

    for p in list(set(args.dir.glob("*.json.gz")) - set(args.dir.glob("*.results.json.gz"))):
        data = gunzip_json(p)
        if data:
            data["completions"] = [c.replace("\t", "    ") for c in data["completions"]]
            with gzip.open(p, "wt") as f:
                json.dump(data, f)
        else:
            print(p)

if __name__ == "__main__":
    main()