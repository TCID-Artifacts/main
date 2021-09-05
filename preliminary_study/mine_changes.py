import requests
import os
import csv
import re

csv_filename = 'candidate_commits.csv'

token = 'gitHub_access_token'

debugPrint = False

with open(csv_filename, newline='') as commit_file:
    reader = csv.DictReader(commit_file, fieldnames=["COMMIT_URL", "HTML_COMMIT_URL"])
    rowCounter=1
    
    changesIdentifiedCounter=0
    
    for row in reader:
        query_url = row["COMMIT_URL"]
        html_url = row["HTML_COMMIT_URL"]
        print('',html_url,' (rowCounter=',rowCounter,')',sep="")
        
    	
        if query_url == "COMMIT_URL":
            continue

        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # , params = params
        page = requests.get(query_url, headers=headers).json()

### various commands to understand the structure of the json files from GitHub
#        print(page)
#        print(type(page)) # should return <class 'dict'> // helpful: https://stackoverflow.com/questions/19490856/navigating-multi-dimensional-json-arrays-in-python
#        for page_item in page:
#            print(page_item)
#            print(type(page_item))
#            if 'files' in page_item:
#                for files_item in page_item:
#                    print(files_item)
#                    print(type(files_item))
###

        numberOfFile=len(page['files'])
        fileIndex=0
        # iterate over the files that were changed as part of this commit
        for file in page['files']:
            if debugPrint: print('***',(fileIndex+1),'of',numberOfFile, 'changed files')
            
            if not 'patch' in file:
                continue
            patch=file['patch']
#            print(patch) # show full patch
            if debugPrint: print(len(patch), 'characters in the patch')
            
            # now do the analysis
            # from co-author: "we're interested in commits that update functions which include a "name" attribute, i.e., describe, fdescribe, xdescribe, test, xtest, it, fit, and xit. At least these are all the ones that have a name attribute according to https://jestjs.io/docs/api."
            patchLines=patch.splitlines()
            if debugPrint: print(len(patchLines),'lines in the patch')
            index=0
            startingIndex=0
            changesFoundInFileCounter=0
            while index<len(patchLines):
                patchLine=patchLines[index]
#                print(patchLine)
                pat = re.compile('^-\s*(describe|fdescribe|xdescribe|test|xtest|it|fit|xit)\(')
                if pat.match(patchLine):
                
                    # keep track of the starting index for reporting purposes
                    startingIndex=index # no "+1" because GitHub commits in the repo count differently
                    changesFoundInFileCounter+=1
                    
                    # print current line
                    print()
                    print(patchLine)
                    
                    patchLineNext=patchLines[index+1]
                    
                    # consume all "- " lines, in case there are any
                    pat = re.compile('^-')
                    while pat.match(patchLineNext):
                        print(patchLineNext)
                        index+=1
                        
                        if len(patchLines)==index+1: break # need to break if the next line is beyond what is in the current patch
                        patchLineNext=patchLines[index+1]
                    
                    # now we should have a line "+ " (unless the entire test was deleted)
#                    pat = re.compile('^\+\s*(describe|fdescribe|xdescribe|test|xtest|it|fit|xit)\(')
                    pat = re.compile('^\+')
                    if pat.match(patchLineNext):
                    
                        # consume all "+ " lines, in case there are any
                        pat = re.compile('^\+')
                        while pat.match(patchLineNext):
                            print(patchLineNext)
                            index+=1
                            if len(patchLines)==index+1: break # need to break if the next line is beyond what is in the current patch
                            patchLineNext=patchLines[index+1]
                        
                        changesIdentifiedCounter+=1
                        print('(changesIdentifiedCounter=',changesIdentifiedCounter,')',sep="")
                        print(\
                            'changes_identified_counter,',changesIdentifiedCounter,','\
                            ,query_url,',',html_url,','\
                            'candidate_commits_csv_row,',rowCounter,','\
                            'changed_files_in_commit,',len(page['files']),','\
                            'file_index_in_commit,',fileIndex,','\
                            'changes_found_in_file_counter,',changesFoundInFileCounter,','\
                            'patch_length,',len(patchLines),','\
                            'test_description_change_index,',startingIndex,','\
                            ,sep="")

                index+=1
            fileIndex+=1

            
        rowCounter+=1
        print() # to separate different commits in the terminal
