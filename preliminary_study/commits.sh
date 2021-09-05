#!/bin/bash
trap "exit" INT TERM ERR
trap "kill 0" EXIT

###########
## RUN THIS ON OUR VIRTUAL ENVIRONMENT!
## $> conda activate tdc3
###########

# remove any unfinished work (in case of CTRL+C)
# rm *part* > /dev/null 2>&1

# split file in several parts (for parallel processing)
fspec=js_projects.csv
num_files=5
total_lines=$(wc -l <${fspec})
((lines_per_file = (total_lines + num_files - 1) / num_files))
# Split the actual file, maintaining lines.
split --lines=${lines_per_file} ${fspec} js_projects_part.

# run processes and store pids in array
pids=() 
for filename in `ls js_projects_part.*`
do
    echo $filename
    # spawn parallel processes in background
    python mine_js_commits.py $filename &
    pids+=( $! )
done

printf '%s\n' "${pids[@]}"

# wait for all pids
for pid in ${pids[*]}; do
    echo "waiting for process $pid to finish"
    wait $pid
done

cat *_part*candidate_commits.csv | sort | uniq > candidate_commits2.csv
# remove parts (tempo)
rm js_projects_part.*
