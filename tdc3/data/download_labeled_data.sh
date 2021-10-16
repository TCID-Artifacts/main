#!/bin/bash

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

# dowload tokenized
echo "Donwloading tokenized"
delete "./labeled_tokenized"
gdown https://drive.google.com/uc?id=1uv-lKj6G36L3oD4P4SX05pNwIMTWPeRH
unzip -q -o labeled_tokenized.zip -d "./"
rm -f labeled_tokenized.zip