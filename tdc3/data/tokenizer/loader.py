from datetime import MAXYEAR
import os
import pandas as pd
import zipfile
import csv
import codecs
from itertools import dropwhile, takewhile
import subprocess
import glob
import tempfile
import shutil

rawdir = os.path.join(os.getcwd(), "raw")

def process_data(filename):
    ## create a tempo directory to store JS files
    tmpdir = tempfile.mkdtemp()    
    first = True
    ## create a json file every 10K
    json_id = 0
    counter = 0
    MAX_counter = 30000
    for pair in pair_generator(filename):
        if first:
            first = False
            continue
        # decrement counter; will create one json when it is done        
        counter += 1
        print((MAX_counter*json_id+counter), end='\r')
        filename = os.path.join(tmpdir, f'_{json_id}_{counter}.js')
        with open(filename, "w") as file:
            file.write("function noname() {\n")
            file.write(pair[1])
            file.write("\n}")
        # create json file with partial results
        if counter == MAX_counter:
            json_id += 1
            counter = 0
            dump_to_file(tmpdir)
    # one last dump remaining
    if not counter == MAX_counter:
        dump_to_file(tmpdir)
    # delete tempo directory
    shutil.rmtree(tmpdir)

def dump_to_file(tmpdir):
    # call node processor     
    subprocess.run(["./tokenize", os.path.join(tmpdir, "*.js"), rawdir])
    # delete all JS files from temporary directory
    for f in glob.glob(tmpdir + '/*.js'):
        os.remove(f)

# we use generators to avoid filling memory with the entire csv.
# that way, only one row needs to be in memory at a time.
def pair_generator(filename):
    zf = zipfile.ZipFile(filename)
    text_files = zf.infolist()
    csv_filename = text_files[0]
    with zf.open(csv_filename, "r") as file:
        for row in csv.reader(codecs.iterdecode(file, 'utf-8')):
            # columns 'Description' and 'Test'
            yield (row[0], row[1])

if __name__ == '__main__' :
    filename = os.path.join(rawdir , 'test_descriptions_raw.zip')
    process_data(filename)
