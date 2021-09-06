from json.decoder import JSONDecodeError
import json
import argparse
from gensim.models.fasttext import FastText
from util.IOUtil import read_files
from nltk.tokenize import word_tokenize


parser = argparse.ArgumentParser()
parser.add_argument(
    "--tokens", help="List of JSON files with token sequences or .txt file with paths of JSON files", required=True, nargs="+")
parser.add_argument(
    "--descriptionmodelfile", help="File to store the description model in after training", required=True)
parser.add_argument(
    "--testmodelfile", help="File to store the test model in after training", required=True)


class TokenSequenceReader(object):
    def __init__(self, data_paths, tokens_type):
        self.data_paths = data_paths
        self.tokens_type = tokens_type

    def __iter__(self):
        for data_path in self.data_paths:
            print("Reading file " + data_path)
            with open(data_path) as file:
                try:
                    all_data = json.load(file)
                    for token_seq in all_data:
                        if self.tokens_type == "description":
                            yield word_tokenize(token_seq["metadata"]["description"])
                        else:
                            yield token_seq["data"]
                except JSONDecodeError as e:
                    print(
                        f"Warning: Ignoring {data_path} due to JSON decode error")


if __name__ == '__main__':
    args = parser.parse_args()

    files = read_files(args.tokens)
    # description model
    description_token_seqs = TokenSequenceReader(files, "description")
    description_model = FastText(description_token_seqs, min_count=3, window=5,
                     size=100, workers=40, iter=15, alpha=0.1, sg=1)
    description_model.save(args.descriptionmodelfile)
    # test model
    test_token_seqs = TokenSequenceReader(files, "test")
    test_model = FastText(test_token_seqs, min_count=3, window=5,
                     size=100, workers=40, iter=15, alpha=0.1, sg=1)
    test_model.save(args.testmodelfile)
    
