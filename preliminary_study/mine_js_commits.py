import requests
import os
import csv
import sys
import random
import time

candidate_commits_filename = 'candidate_commits.csv'

token1 = 'gitHub_access_token1'
token2 = 'gitHub_access_token2'
tokens = [token1, token2]
token = random.choice(tokens)
# per project. for example (pagesize=300 and numpages=1) means it returns 1 page with 300 commits per project
pagesize = 100 # (max size is 100)
numpages = 2

def rotate_token():
    global token
    if token == token1:
        token = token2
    else:
        token = token1


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def main(projects_filename):
    columns = ["COMMIT_URL", "HTML_COMMIT_URL"]
    num_lines = file_len(projects_filename)
    with open(projects_filename, newline='') as csvfile, open(projects_filename+candidate_commits_filename, 'w') as commitFile:
        # candidate commits
        writer = csv.writer(commitFile)
        writer.writerow(columns)
        # candidate projects
        reader = csv.DictReader(csvfile, fieldnames=['Project_name','URL'])
        project_counter = 0
        project_with_interestingcommits = 0
        for row in reader:
            # processing a given project
            name = row['Project_name']
            url = row['URL']
            if name == 'Project_name':
                continue
            project_counter += 1
            # page number i
            num_commits = 0
            num_interesting_commits = 0
            for i in range(1, numpages + 1):
                query_url = f"https://api.github.com/repos/{name}/commits" # name has format {project}/{owner}
                params = {
                    "page": i,
                    "per_page": pagesize
                }
                headers = {
                    'Authorization': f'token {token}',
                    'Accept': 'application/vnd.github.v3+json'
                }
                try:
                    data = requests.get(query_url, headers=headers, params=params)
                except requests.exceptions.ConnectionError:
                    print("CONNECTION PROBLEM. Likely rate limit reached. Sleeping for 10m...")
                    time.sleep(600) # 10 minutes
                    rotate_token()
                    break
                try:
                    page = data.json()
                except ValueError:
                    print(data)
                    # can't parse json. probably no data.
                    continue
                # page has several item, each item is a different commit
                print(query_url + f", page {i}")
                for page_item in page:
                    num_commits += 1
                    if not 'commit' in page_item:
                        print('CHECK! commit not in page_item')
                        print(page_item)
                        print(page)
                        rotate_token()
                        break
                    commit = page_item['commit']
                    if not 'message' in commit:
                        print('CHECK! message not in page_item[commit]')
                        print(commit)
                        break
                    msg = commit['message']
                    # downloading string and checking that "test string" appears led to best results
                    if 'test description' in msg:
                        num_interesting_commits += 1
                        project_with_interestingcommits += 1
                        row = [page_item['url'], page_item['html_url']]
                        writer.writerow(row)
            if project_counter % 100 == 0:
                print(f'projects with interesting commits: {project_with_interestingcommits}, projects processed {project_counter} out of {num_lines}')
            # print(f'{name} with {num_commits} commits and {num_interesting_commits} interesting commits')


if __name__ == '__main__':
    # print command line arguments
    # for arg in sys.argv[1:]:
    #     print(arg)
    main(projects_filename=sys.argv[1])
