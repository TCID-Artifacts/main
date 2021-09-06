import os
import csv
import subprocess
import pandas as pd
import argparse
import time

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--firstprojectindex", 
    help="Index of project, from javaScript_projects.csv file, to start colecting pairs", 
    required=True)
parser.add_argument(
    "--lastprojectindex", 
    help="Index of project, from javaScript_projects.csv file, to end colecting pairs", 
    required=True)

args = parser.parse_args()

# create projects directory
process = subprocess.Popen("mkdir test_descriptions_finder/projects", shell=True)
process.wait()

# create parser output directory
process = subprocess.Popen("mkdir test_descriptions_finder/parser/output", shell=True)
process.wait()

counter = 0
file_index = int(args.firstprojectindex) - 1
# Each CSV file contains 1000 pairs
dump_pairs = 1000

columns = ["Description", "Test", "Project_name", "File"]
rows = []

javaScript_projects = pd.read_csv("git_miner/javaScript_projects.csv")

# find test descriptions for each test of each project
for index in range(int(args.firstprojectindex) - 1, int(args.lastprojectindex)):
	project_name = javaScript_projects.iloc[index]["Project_name"]

	if project_name.split("/")[-1][0] != ".":
		project_url = javaScript_projects.iloc[index]["URL"]

		# log info
		print("=================================================")
		print("Collecting pairs from project " + str(index + 1))

		# clone project
		process = subprocess.Popen("cd test_descriptions_finder/projects && git clone --depth 1 " + project_url, shell=True)
		process.wait()

	        # find javascript test files and send to test_files.txt
		process = subprocess.Popen("cd test_descriptions_finder/projects && find . -type f -name '*.js' -exec grep -l 'describe(' {} \\; >> ../test_files.txt", shell=True)
		process.wait()

	        # store the name of JS files containing tests
		test_files = open("test_descriptions_finder/test_files.txt", "r")

		for file in test_files:
			formated_file_path = file[1:].strip('\n')

			if " " not in formated_file_path:
				# remove lines with import and export 
				process = subprocess.Popen("grep -v 'import' test_descriptions_finder/projects" + formated_file_path + " > temp && mv temp test_descriptions_finder/projects" + formated_file_path, shell=True)
				process.wait()

				process = subprocess.Popen("grep -v 'export' test_descriptions_finder/projects" + formated_file_path + " > temp && mv temp test_descriptions_finder/projects" + formated_file_path, shell=True)
				process.wait()

				# select (description, test) pairs
				process = subprocess.Popen("cd test_descriptions_finder/parser && node visitor.js ../projects" + formated_file_path, shell=True)
				process.wait()

				for root, dirs, files in os.walk("test_descriptions_finder/parser/output"):
					for file in files:
						with open(root + os.sep + file, 'r') as fd:
							descriptionFlag = 0
							testFlag = 0

							description = ""
							test = ""

							for line in fd:
								if (line == "//text\n"):
									descriptionFlag = 1
								elif (line == "//test\n"):
									descriptionFlag = 0
									testFlag = 1
								else:
									if descriptionFlag:
										description += line
									else:
										test += line

							file_path = formated_file_path.split("/")[2:]
							file_url = project_url + "/blob/master/" + "/".join(file_path)
							rows.append([description, test, project_name, file_url])
							counter += 1

							if (counter == dump_pairs):
								with open('../scraped/test_descriptions_raw_' + str(file_index) + '.csv', 'a') as csvFile:
									writer = csv.writer(csvFile)
									writer.writerow(columns)
									writer.writerows(rows)

								rows = []
								counter = 0
								file_index += 1

		                # delete JS files with pairs
				process = subprocess.Popen("cd test_descriptions_finder/parser/output && rm -rf ./*", shell=True)
				process.wait()

		# delete test files
		process = subprocess.Popen("rm test_descriptions_finder/test_files.txt", shell=True)
		process.wait()

		# delete project directory
		process = subprocess.Popen("cd test_descriptions_finder/projects && rm -rf ./*", shell=True)
		process.wait()

# delete projects directory
process = subprocess.Popen("cd test_descriptions_finder && rm -rf projects", shell=True)
process.wait()

# save exceeding pairs
if (len(rows)):
	with open('../scraped/test_descriptions_raw_exceeding' + str(file_index) + '.csv', 'a') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(columns)
		writer.writerows(rows)

print(f"It took {time.time() - start_time} seconds to find {(file_index - int(args.firstprojectindex) - 1) * dump_pairs} pairs")

	



