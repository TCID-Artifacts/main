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
from py.models.EnsembleModel import Ensemble
from py.data.TestDescriptionConsistencyHumanLabeledDataset import TestDescriptionConsistencyHumanLabeledDataset
from py.util.Config import device, lr, epochs
from py.models.Training import Training
from py.models.Validation import Validation
from py.data.TokensPerFunctionData import group_by_nb_calls

import matplotlib.pyplot as plt
import numpy as np
import nltk
import pandas as pd

batch_size = 10

parser = argparse.ArgumentParser()
parser.add_argument(
    "--description_embedding", help="Pre-trained description token embedding", required=True)
parser.add_argument(
    "--test_embedding", help="Pre-trained test token embedding", required=True)
parser.add_argument(
    "--consistent_data", help="Directory with JSON files containing human labelled consistent examples", nargs=1)
parser.add_argument(
    "--inconsistent_data", help="Directory with JSON files containing human labelled inconsistent examples", nargs=1)
parser.add_argument(
    "--max_body_length", help="Maximum length of the test body", required=True)
parser.add_argument(
    "--max_description_length", help="Maximum length of the test description", required=True)
parser.add_argument(
    "--load_model", help="Load a trained model from the given file", nargs=1)

def create_dataloader(consistent_json_dataset, inconsistent_json_dataset, 
    description_embedding, test_embedding, embedding_size, max_body_length, 
    max_description_length, save_path=None):
    dataset = TestDescriptionConsistencyHumanLabeledDataset(
    	description_embedding, test_embedding, embedding_size, 
        max_body_length, max_description_length)
    dataset.prepare_data(consistent_json_dataset, inconsistent_json_dataset)
    if save_path != None:
        dataset.save_to_disk(save_path[0])
    dataset.move_to_target_device()
    return DataLoader(dataset, batch_size=batch_size, shuffle=True)

def analyze_predictions(all_predictions, json_dataset, model_type):
    df = pd.DataFrame(all_predictions, columns=["id", "label", "prediction"])
    df.sort_values(by=["id"], inplace=True)
    df.to_csv(f"predictions_{model_type}.csv", index=False)

if __name__ == "__main__":
    nltk.download('punkt')
    nltk.download('stopwords')

    args = parser.parse_args()

    print(args.consistent_data)

    print("Loading pre-trained token embeddings")
    description_embedding = FastText.load(args.description_embedding)
    test_embedding = FastText.load(args.test_embedding)
    embedding_size = len(test_embedding["test"])
    max_body_length = int(args.max_body_length)
    max_description_length = int(args.max_description_length)

    executions = [1]
    training_sizes = [0]

    for execution in executions:

        for training_size in training_sizes:

            print("Loading labelled data")
            consistent_data_files = json_files_in_dir(args.consistent_data[0])
            consistent_json_dataset = JSONInMemoryDataset(consistent_data_files)
            consistent_json_train_dataset, consistent_json_validate_dataset = split_dataset(
                    consistent_json_dataset, training_size)

            inconsistent_data_files = json_files_in_dir(args.inconsistent_data[0])
            inconsistent_json_dataset = JSONInMemoryDataset(inconsistent_data_files)
            inconsistent_json_train_dataset, inconsistent_json_validate_dataset = split_dataset(
                    inconsistent_json_dataset, training_size)

            validate_loader = create_dataloader(
                consistent_json_validate_dataset, inconsistent_json_validate_dataset, 
                description_embedding, test_embedding, embedding_size, max_body_length, 
                max_description_length)

            criterion = BCELoss()  # binary cross entropy

            print(f"Loading a trained model from {args.load_model[0]}")
            model = TransformerModel(embedding_size)
            #model = FunctionNameConsistencyModel(embedding_size)
            model.load_state_dict(t.load(args.load_model[0], map_location=t.device('cpu')))
            model.to(device)
            
            validation = Validation(
                    model, criterion, validate_loader, batch_size, max_body_length)

            for t in [0.5, 0.3, 0.1]:
                all_predictions = validation.run(t, epoch=9, training_size=training_size, execution=execution, store_all_predictions=True)
            # analyze_predictions(all_predictions, inconsistent_json_validate_dataset, "ensembled")

            validation.save_data()

          