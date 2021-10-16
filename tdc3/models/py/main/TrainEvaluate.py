import sys
import argparse
from os.path import isdir
import torch as t
from torch.utils.data import DataLoader
from torch.nn import BCELoss
from torch.optim import Adam, SGD
from gensim.models.fasttext import FastText

from py.data.JSONInMemoryDataset import JSONInMemoryDataset
from py.data.Util import json_files_in_dir, split_dataset
from py.models.FunctionNameConsistencyModel import FunctionNameConsistencyModel
from py.models.TransformerModel import TransformerModel
from py.data.FunctionNameConsistencyDataset import FunctionNameConsistencyDataset
from py.util.Config import device, batch_size, lr, epochs
from py.models.Training import Training
from py.models.Validation import Validation
from py.data.TokensPerFunctionData import group_by_nb_calls

import matplotlib.pyplot as plt
import numpy as np
import nltk
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument(
    "--description_embedding", help="Pre-trained description token embedding", required=True)
parser.add_argument(
    "--test_embedding", help="Pre-trained test token embedding", required=True)
parser.add_argument(
    "--data", help="Directory with JSON files to use for training and validation, or paths to pre-computed training and validation data", nargs="+", required=True)
parser.add_argument(
    "--max_body_length", help="Maximum length of the test body", required=True)
parser.add_argument(
    "--max_description_length", help="Maximum length of the test description", required=True)
parser.add_argument(
    "--store_train_data", help="Store the prepared training dataset into the given file", nargs=1)
parser.add_argument(
    "--store_validate_data", help="Store the prepared validation dataset into the given file", nargs=1)
parser.add_argument(
    "--store_model", help="Store the trained model into the given file", nargs=1)
parser.add_argument(
    "--load_model", help="Load a trained model from the given file and perform validation only.", nargs=1)


def create_dataloader(json_dataset, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length, save_path=None):
    dataset = FunctionNameConsistencyDataset(
    description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
    dataset.prepare_data(json_dataset)
    if save_path != None:
        dataset.save_to_disk(save_path[0])
    dataset.move_to_target_device()
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def load_stored_data(filename, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length):
    dataset = FunctionNameConsistencyDataset(
        description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
    dataset.load_from_disk(filename)
    dataset.move_to_target_device()
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)


def analyze_predictions(all_predictions, json_dataset):
    id_to_item = {}
    for item in json_dataset:
        id_to_item[item["id"]] = item

    df = pd.DataFrame(all_predictions, columns=["id", "label", "prediction"])
    df.sort_values(by=["prediction"], inplace=True)
    is_positive = df["label"] == 1
    is_warning = df["prediction"] < 0.5
    warnings = df[is_positive & is_warning]

    for index, w in warnings.iterrows():
        item = id_to_item[w["id"]]
        print(f"\n----------\nWarning with p={w['prediction']} -- id={w['id']}")
        print(item["metadata"]["description"])
        print("##")
        print(" ".join(item["data"]))


if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')

    args = parser.parse_args()

    print("Loading pre-trained token embeddings")
    description_embedding = FastText.load(args.description_embedding)
    test_embedding = FastText.load(args.test_embedding)
    embedding_size = len(test_embedding["test"])
    max_body_length = int(args.max_body_length)
    max_description_length = int(args.max_description_length)

    if len(args.data) == 1:
        # load data from JSON
        data_files = json_files_in_dir(args.data[0])
        print(f"Loading data from {len(data_files)} JSON files")
        json_dataset = JSONInMemoryDataset(data_files)
        json_train_dataset, json_validate_dataset = split_dataset(
            json_dataset, 0.8)

        train_loader = create_dataloader(
            json_train_dataset, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length, args.store_train_data)

        validate_loader = create_dataloader(
            json_validate_dataset, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length, args.store_validate_data)
    elif len(args.data) == 2:
        train_loader = load_stored_data(
            args.data[0],  description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
        validate_loader = load_stored_data(
            args.data[1],  description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
    elif len(args.data) == 3:
        train_loader = load_stored_data(
            args.data[0],  description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
        validate_loader = load_stored_data(
            args.data[1],  description_embedding, test_embedding, embedding_size, max_body_length, max_description_length)
        data_files = json_files_in_dir(args.data[2])
        print(f"Loading data from {len(data_files)} JSON files")
        json_dataset = JSONInMemoryDataset(data_files)
    else:
        print(f"Must pass 1, 2, or 3 data arguments, but not {len(args.data)}")

    criterion = BCELoss()  # binary cross entropy
    if args.load_model is None:
        print(f"Training the classification model")
        #model = FunctionNameConsistencyModel(embedding_size).to(device)
        model = TransformerModel(embedding_size).to(device)
        optimizer = Adam(model.parameters(), lr=lr)

        training = Training(model, criterion, optimizer,
                            train_loader, batch_size, epochs)
        validation = Validation(
            model, criterion, validate_loader, batch_size, max_body_length)

        training.run("transformer_model", validation=validation)
    else:
        print(f"Loading a trained model from {args.load_model[0]}")
        #model = FunctionNameConsistencyModel(embedding_size)
        model = TransformerModel(embedding_size)
        model.load_state_dict(t.load(args.load_model[0]))
        model.to(device)

        validation = Validation(
            model, criterion, validate_loader, batch_size, max_body_length)
        all_predictions = validation.run(0.5, store_all_predictions=True)
        analyze_predictions(all_predictions, json_dataset)

    validation.save_data()
    validation.plot(model, validate_loader)