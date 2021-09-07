import os
import argparse
import torch as t
from py.util.Config import dtype
from py.models.FunctionNameConsistencyModel import FunctionNameConsistencyModel
from py.models.TransformerModel import TransformerModel
from py.data.FunctionNameConsistencyDataset import en_stops, Embedding
from py.data.JSONInMemoryDataset import JSONInMemoryDataset
from py.data.Util import json_files_in_dir
from py.util.Config import device
from gensim.models.fasttext import FastText
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument(
    "--CSV_file", help="File with raw pairs", required=True)
parser.add_argument(
    "--JSON_dir", help="Directory with jsons containing tokenized test body(ies)", required=True)
parser.add_argument(
    "--description_embedding", help="Pre-trained description token embedding", required=True)
parser.add_argument(
    "--test_embedding", help="Pre-trained test token embedding", required=True)
parser.add_argument(
    "--max_body_length", help="Maximum length of the test body", required=True)
parser.add_argument(
    "--max_description_length", help="Maximum length of the test description", required=True)
parser.add_argument(
    "--classification_model", help="Pre-trained classification model", required=True)

def token_to_body_tensor(tokens, emb, emb_size, max_body_length):
    body_vec = []
    for token in tokens[:max_body_length]:
        if token not in en_stops:
            body_vec.append(emb.get(token))
    while len(body_vec) < max_body_length:
        body_vec.append([0] * emb_size)
    return t.as_tensor(body_vec, dtype=dtype, device="cpu")

def string_to_desc_tensor(test_description, emb, emb_size, max_description_length):
    description_vec = []
    for token in word_tokenize(test_description)[:max_description_length]:
        if token not in en_stops:
            description_vec.append(emb.get(token))
        while len(description_vec) < max_description_length:
            description_vec.append([0] * emb_size)
    return t.as_tensor(description_vec, dtype=dtype, device="cpu")

if __name__ == "__main__":

    args = parser.parse_args()

    print("Loading pre-trained token embeddings")
    description_embedding = FastText.load(args.description_embedding)
    test_embedding = FastText.load(args.test_embedding)
    embedding_size = len(test_embedding["test"])
    
    de = Embedding(description_embedding)
    te = Embedding(test_embedding)

    max_body_length = int(args.max_body_length)
    max_description_length = int(args.max_description_length)

    print("Loading the classification model")
    model = TransformerModel(embedding_size)
    model.load_state_dict(t.load(args.classification_model, map_location=t.device('cpu')))
    model.to(device)

    print("Loading input...")
    data_files = json_files_in_dir(args.JSON_dir)
    json_dataset = JSONInMemoryDataset(data_files)

    print("Evaluating input...")
    dataframe = pd.read_csv(args.CSV_file)
    dataframe["TDC3Prediction"] = ""

    for idx in range(len(json_dataset)):
        token_seq = json_dataset[idx]
        body_tokens = token_seq["data"]
        body_tensor = token_to_body_tensor(body_tokens, emb=te, emb_size=embedding_size, max_body_length=max_body_length)

        desc_str = token_seq["metadata"]["description"]
        desc_tensor = string_to_desc_tensor(desc_str, emb=de, emb_size=embedding_size, max_description_length=max_description_length)

        with t.no_grad():
            model.eval()

            # need to change dimensions as the model accepts as
            # input a batch of examples
            # body: tensor(#BATCH * 10 * 100)
            # desc: tensor(#BATCH * 100)

            body_dim = list(body_tensor.size())
            body_view = body_tensor.view(-1, body_dim[0], body_dim[1])

            desc_dim = list(desc_tensor.size())
            desc_view = desc_tensor.view(-1, desc_dim[0], desc_dim[1])

            xs_view = (body_view, desc_view)

            # batch with a single input
            prediction = model(xs_view)
            prediction_single = prediction.numpy()[0][0]

            dataframe.at[idx, "TDC3Prediction"] = prediction_single

    dataframe.to_csv(args.CSV_file, index=False)
