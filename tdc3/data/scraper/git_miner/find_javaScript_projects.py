import requests
import time
import csv
import pandas as pd
import argparse
import time
import os

start_time = time.time()

parser = argparse.ArgumentParser()
parser.add_argument(
    "--minprojectsize", 
    help="Minimum project size (in kilobytes) to search on GitHub", 
    required=True)
parser.add_argument(
    "--maxprojectsize", 
    help="Maximum project size (in kilobytes) to search on GitHub", 
    required=True)

args = parser.parse_args()

# Create CSV file and add header if it doesn't exist 
if not os.path.isfile('git_miner/javaScript_projects.csv'):
	columns = ["Project_name", "URL"]

	with open('git_miner/javaScript_projects.csv', 'a') as csvFile:
		writer = csv.writer(csvFile)
		writer.writerow(columns)

	previous_found_projects = 0
else:
	df = pd.read_csv("git_miner/javaScript_projects.csv")
	previous_found_projects = df.shape[0]

# Size of repositories
min_size = int(args.minprojectsize)
max_size = int(args.maxprojectsize)

# We can search until max_size < 1000000
while (min_size < max_size):
	# log info
	print(f"Searching projects with at least {min_size} and at most {min_size + 1} kilobytes")

	i=1
	
	while(True):
		row = []
		# (Estimate) maximum of pages
		if (i > 100):
			break

		time.sleep(10)
		url = f"https://api.github.com/search/repositories?q=jest+is:public+size:{min_size}..{min_size + 1}+language:JavaScript&page={i}"
		user_data = requests.get(url).json()
		j = 0

		# Each page has 30 repositories
		while (j < 30):
			try:
				name=(user_data['items'][j]).get('full_name')
				url=(user_data['items'][j]).get('html_url')
								
				row = [name, url]
				print(row)
				with open('git_miner/javaScript_projects.csv', 'a') as csvFile:
					writer = csv.writer(csvFile)
					writer.writerow(row)
			except:
				pass

			j += 1

		i += 1
		
		if(len(row) == 0): # break out if nothing is returned
			break

	min_size += 1

# Remove duplicate rows
df = pd.read_csv("git_miner/javaScript_projects.csv")
df.drop_duplicates(subset=None, inplace=True)
df.to_csv("git_miner/javaScript_projects.csv", index=False)

# Remove repositories that are not public
public=[]
df = pd.read_csv("git_miner/javaScript_projects.csv")
for index in df.iterrows():
    if(requests.get(index[1]['URL']).status_code == 200):
    	print (index[1]['URL'] + " is publicly accesible...")
    	public.append(index[1])
df2=pd.DataFrame(public,columns = ["Project_name", "URL"])
df2.to_csv("git_miner/javaScript_projects.csv", index=False)

print(f"It took {time.time() - start_time} seconds to find {df.shape[0] - previous_found_projects} projects")
