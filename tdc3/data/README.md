## Data

This directory contains the services to collect and prepare our dataset. We use these services in the following order:

scraper => filter => tokenizer => embedder

## Directory Structure

A star (*) preceding the name of a directory indicates that that directory is *not* under version control. Those directories are created by extracting the contents from large zip files (that is why they are not under version control) stored on our Google Drive.

<b>scraper</b>: contains the source code for scraping GitHub for pairs of jest (JS test format) descriptions and bodies. The scrapper outputs CSV files with unprocessed pairs of test descriptions and corresponding bodies.

<b>*scraped</b>: contains the csv files produced by the scraper.

<b>filter</b>: contains the source code for filtering pairs of jest tests descriptions and bodies that are not empty and whose description is in English. The filter receives the files on scrapped as input and outputs CSV files with processed pairs of test descriptions and corresponding bodies.

<b>*filtered</b>: contains the csv files produced by the filter.

<b>tokenizer</b>: contains the source code for tokenizing pairs of test description and test body code. The tokenizer receives the files on filtered and produces JSON files (with pairs of test description and corresponding list of tokens for the test body). 

<b>*tokenized</b>: contains the JSON files, produced by the tokenizer, with pairs of test description and their *tokenized* bodies.

<b>embedder</b>: contains the source code for creating the embedder. The embedder receives the files on tokenized as input and outputs a FastText Python embedder/vectorizer.

<b>*embedded</b>: contains the FasText Python embedder/vectorizer. 

## Download Files

To use the data we mined and prepared, run:

```
./download_data.sh
```

## Steps to Reproduce

If you want to mine and prepare the data yourself (it can take hours/days), i.e., to scrape GitHub for tests, tokenize the test code, and train an embedder, read the README.md file in the corresponding directory of each service in the following order:

1. To see how to produce scraped, check scraper/README.md.

2. To see how to produce filtered, check filter/README.md.

3. To see how to produce tokenized, check tokenizer/README.md.

4. To see how to produce embedded, check embedder/README.md.







