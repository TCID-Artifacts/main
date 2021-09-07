import argparse
import json
from py.data.Util import json_files_in_dir

parser = argparse.ArgumentParser(description="Given a set of JSON files, adds a unique 'id' field to each item in the files.")
parser.add_argument(
    "--data", help="Directory with JSON files.", nargs="+", required=True)

if __name__ == "__main__":
    args = parser.parse_args()
    data_files = json_files_in_dir(args.data[0])
    next_id = 1
    for f in data_files:
        with open(f) as fp:
            items = json.load(fp)
        for item in items:
            item['id'] = next_id
            next_id += 1
        with open(f, "w") as fp:
            json.dump(items, fp, indent=2)
