import fasttext
import csv
import os
import sys
import time
import argparse

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--inputdir", help="Directory with CSVs containing pairs to be filtered", required=True)
parser.add_argument(
    "--outputdir", help="Directory with CSVs containing filtered pairs", required=True)
args = parser.parse_args()

csv.field_size_limit(sys.maxsize)

this_file_dir = os.path.dirname(os.path.realpath(__file__))
# filtered_dir = os.path.join(this_file_dir, args.outputdir)
# scraped_dir = os.path.join(this_file_dir, args.inputdir)
scraped_dir = args.inputdir
filtered_dir = args.outputdir
PRETRAINED_MODEL_PATH = os.path.join(this_file_dir, 'lid.176.bin')
model = fasttext.load_model(PRETRAINED_MODEL_PATH)

def getstuff(filename):
    with open(filename, "rt", encoding="utf8") as csvfile:
        datareader = csv.reader(csvfile)
        count = 0
        for row in datareader:
            yield row

total_filtered_rows = 0
for root, dirs, files in os.walk(scraped_dir): # consider replacing with scraped_dir/*.csv to be safe
    for filename in files:
        filtered_rows_per_file = 0
        print(f"file to filter: {filename}")
        outfile = os.path.join(filtered_dir, filename.replace("raw", "filtered"))
        print(f"filtered file: {outfile}")

        # reading csv as stream to avoid blocking (exhausting resources)
        for row in getstuff(os.path.join(root, filename)):

            description = row[0].replace('\n', ' ').replace('\r', '').strip()
            test = row[1].replace('\n', ' ').replace('\r', '').strip()

            # Neither the description nor the test is empty
            if description and test:

                predictions = model.predict(description)

                # English with any probability or non-english with up to 15% probability
                if str(*(predictions[0])).endswith("en") or predictions[1].item() <= 0.15:
                    with open(outfile, 'a') as target:
                        writer = csv.writer(target)
                        writer.writerow(row)
                        total_filtered_rows += 1
                        filtered_rows_per_file += 1
                        print(f"Num Rows appended to file: {filtered_rows_per_file}\r", end="", flush=True)

print(f"It took {time.time() - start_time} seconds to filter {total_filtered_rows} pairs")