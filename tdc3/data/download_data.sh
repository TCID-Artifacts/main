#!/bin/bash

# using python's gdown to download file. strange behavior in wget and
# curl that cannot handle some URL generated by Google Drive
pip install gdown

delete(){
    DIR=$1
    mkdir -p $DIR # creates if does not exist
    if [ -d $DIR ] 
    then
	(cd $DIR;
	 rm * 2> /dev/null
	)
    else
	echo "cannot find directory $DIR"
    fi    
}

# download scraped
echo "Downloading scraped"
delete "./scraped"
gdown https://drive.google.com/uc?id=1NUhJCwQmE-EgXy-J0rl-swtvti4798qP
unzip -q -o scraped.zip -d "./"
rm -f scraped.zip

# dowload filtered
echo "Donwloading filtered"
delete "./filtered"
gdown https://drive.google.com/uc?id=1LSmDYZWFaxJXniK7AanrK33e29huvNh_
unzip -q -o filtered.zip -d "./"
rm -f filtered.zip

# dowload tokenized
echo "Donwloading tokenized"
delete "./tokenized"
gdown https://drive.google.com/uc?id=1RUMH_BvhBod6Mna0t_XFP2XCMZSVwkkn
unzip -q -o tokenized.zip -d "./"
rm -f tokenized.zip

# download embedded
echo "Donwloading embedded"
delete "./embedded"
gdown https://drive.google.com/uc?id=18DJyxG_q2L8-pfj3mxskYXVqAs8cei1h
unzip -q -o embedded.zip -d "./"
rm -f embedded.zip