Observations:
 - To run the scripts below you will need to activate the conda environment for the project. There is a script in the root directory to create the "tdc3" environment. After that, run the following command.
 
  $> conda activate tdc3

 - IMPORTANTE! In our scripts, we used two Github tokens of two co-authors hardcoded. To reproduce results, replace 'gitHub_access_token' by a GitHub access token. 

 - Unless you want to collect more projects and/or more commits from
those projects, there is no need to run steps 1 and 2 again as the
files they generate are already stored in the repo.

Instructions:

1. Mine JS projects

$> python mine_js_projects.py

obs.this script generates the file javascript_projects.csv containing
JS projects (aprox. evenly distributed across years 2010-2021) with
100+ stars

2. Mine commits from those JS files

$> python mine_js_commits.py javascript_projects.csv

obs. 1. this script downloads a specified number of commits for each
one of those projects, checking which ones contain the string "test
description". Check rationale in paper.

obs. 2. made the project file a parameter to enable parallelization of
this script. you can split the original file in parts and call the
script many times, but it is important to have more tokens.

3. Mine test description changes

obs. this script analyzes each commit and report the number of
tests whose descriptions were actually changed.