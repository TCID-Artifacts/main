## Scraper

This directory contains the source code to mine GitHub repositories written in JavaScript and using [Jest](https://jestjs.io/).

## Steps to run: 

1. python3 git_miner/find_javaScript_projects.py --minprojectsize v1 --maxprojectsize v2
2. mkdir ../scraped
3. cd test_descriptions_finder/parser && npm install && cd ../..
4. python3 test_descriptions_finder/finder.py --firstprojectindex v1 --lastprojectindex v2

Notes: 

Steps 1 and 4 take too long to run. Instead of running them at once, we can indicate the search space through arguments:

* On step 1, v1 and v2, indicate the project size range to search on GitHub. E.g. To find projects with at least 0 and at most 2 kilobytes, v1 and v2 would be 0 and 2, respectively.

* On step 4, v1 and v2, are indexes of projects on the git_miner/javaScript_projects.csv file. E.g. If you want to collect data for the 10 first projects, v1 and v2 would be 1 and 10, respectively.

