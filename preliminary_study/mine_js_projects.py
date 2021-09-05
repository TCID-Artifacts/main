import requests
import csv
import pandas as pd
import os
import time
import sys

#TODO: This script may report project slugs multiple times

## constants
csv_filename = 'javascript_projects.csv'

token1 = 'gitHub_access_token1'
token2 = 'gitHub_access_token2'
token = token1
page_size = 100
num_pages = 10 # 20 pages with $page_size project repositories each
num_stars = 100 # no less than $num_stars stars
language = "javascript"

def rotate_token():
    global token
    if token == token1:
        token = token2
    else:
        token = token1


def main(size):
    print(f"searching size {size}")

    if not os.path.isfile(csv_filename):
        columns = ["Project_name", "URL"]
        with open(csv_filename, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerow(columns)
        previous_found_projects = 0
    else:
        df = pd.read_csv(csv_filename)
        previous_found_projects = df.shape[0]

    # dates = []
    # for year in range(2010, 2022):
    #     for month in range(1, 13):
    #         month_with_leading_zeros = f'0{month}'[-2:]
    #         day = 30
    #         if month == 2:
    #             day = 27
    #         dates.append(f'{year}-{month_with_leading_zeros}-{day}..{year}-{month_with_leading_zeros}-{day}')

    # for year in range(2010, 2022):
    for i in range(1, num_pages+1):
        print(i)
        #Documentation: https://docs.github.com/en/rest/reference/search#search-repositories
        params = {
            "page": i,
            "per_page": page_size
            # "size": size
        }
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # +created:{year}..{year+1}
        query_url = f"https://api.github.com/search/repositories?q=is:public+language:{language}+stars:>={num_stars}+size:{size}"
        repo_json = requests.get(query_url, headers=headers, params=params).json()
        if not 'items' in repo_json:
            if repo_json['message'] == 'Only the first 1000 search results are available':
                print(f"1K results per query limit reached for this query. moving to a different date range (new query).")
                break
            if repo_json['message'].startswith('API rate limit exceeded for user'):
                print("rate limit exceeded. rotating token. sleep for 60s.")
                time.sleep(60)
                rotate_token()
                continue
            print(f'SHOULD NOT HAPPEN! {repo_json["message"]}')
            break
        items = repo_json['items']
        if len(items) == 0:
            print(f"no more results for.")
            break
        for item in items:
            try:
                name = item.get('full_name')
                url = item.get('html_url')
                row = [name, url]
                if len(row) == 0:  # break out if nothing is returned
                    break
                with open(csv_filename, 'a') as csvFile:
                    writer = csv.writer(csvFile)
                    writer.writerow(row)
            except:
                pass

if __name__ == '__main__':
    # print command line arguments
    # for arg in sys.argv[1:]:
    #     print(arg)
    main(size=sys.argv[1])
