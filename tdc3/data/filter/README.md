## Filter

This directory contains the source code to filter pairs whose description or test body is not empty and with description written in English, using [fastText](https://fasttext.cc/).

## Steps to run: 

1. mkdir ../filtered
2. wget https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
3. ./run ../scraped ../filtered