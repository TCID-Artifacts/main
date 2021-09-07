import argparse
from os.path import isdir
import torch as t
import torch
from torch.utils.data import DataLoader
from torch.nn import BCELoss
from torch.optim import Adam, SGD
from gensim.models.fasttext import FastText

from py.data.JSONInMemoryDataset import JSONInMemoryDataset
from py.data.Util import json_files_in_dir, split_dataset
from py.models.FunctionNameConsistencyModel import FunctionNameConsistencyModel
from py.models.TransformerModel import TransformerModel
from py.data.TestDescriptionConsistencyHumanLabeledDataset import TestDescriptionConsistencyHumanLabeledDataset
from py.util.Config import device, lr, epochs, k_folds
from py.models.TrainingKFold import TrainingKFold
from py.models.ValidationKFold import ValidationKFold
from py.data.TokensPerFunctionData import group_by_nb_calls
from py.models.EnsembleModel import Ensemble

import matplotlib.pyplot as plt
import numpy as np
import nltk
import pandas as pd

from sklearn.model_selection import StratifiedKFold

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
    "--store_model", help="Store the trained model into the given file", nargs=1)
parser.add_argument(
    "--load_model", help="Load a trained model from the given file and train on more data", nargs=1)

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

    print("Loading labelled data")
    consistent_data_files = json_files_in_dir(args.consistent_data[0])
    consistent_json_dataset = JSONInMemoryDataset(consistent_data_files)

    inconsistent_data_files = json_files_in_dir(args.inconsistent_data[0])
    inconsistent_json_dataset = JSONInMemoryDataset(inconsistent_data_files)

    #dataset_sizes = [0.25, 0.50, 0.75, 1]
    dataset_sizes = [1]

    for dataset_size in dataset_sizes:
        # Randonly select samples with specific sizes from the full dataset
        consistent_json_dataset_, _ = split_dataset(
                    consistent_json_dataset, dataset_size)

        inconsistent_json_dataset_, _ = split_dataset(
                    inconsistent_json_dataset, dataset_size)

        dataset = TestDescriptionConsistencyHumanLabeledDataset(
            description_embedding, test_embedding, embedding_size, 
            max_body_length, max_description_length)
        dataset.prepare_data(consistent_json_dataset_, inconsistent_json_dataset_)

        skf = StratifiedKFold(n_splits=k_folds, shuffle=True)
                    
        # Start print
        print('--------------------------------')

        # StratifiedKFold Cross Validation model evaluation
        for fold, (train_ids, test_ids) in enumerate(skf.split(np.zeros(2*len(consistent_json_dataset_)), dataset.is_consistent_tensors)):
            print(f'FOLD {fold}')
            print('--------------------------------')
                    
            # Sample elements randomly from a given list of ids, no replacement.
            train_subsampler = torch.utils.data.SubsetRandomSampler(train_ids)
            test_subsampler = torch.utils.data.SubsetRandomSampler(test_ids)
                    
            # Define data loaders for training and testing data in this fold
            train_loader = torch.utils.data.DataLoader(
                dataset, 
                batch_size=batch_size, sampler=train_subsampler)
            validate_loader = torch.utils.data.DataLoader(
                dataset,
                batch_size=batch_size, sampler=test_subsampler)

            print(f"Loading a trained model from {args.load_model[0]}")
            #model = FunctionNameConsistencyModel(embedding_size)
            model = TransformerModel(embedding_size)
            model.load_state_dict(t.load(args.load_model[0], map_location=torch.device('cpu')))
            model.to(device)

            optimizer = Adam(model.parameters(), lr=lr)
            criterion = BCELoss()  # binary cross entropy

            training = TrainingKFold(model, criterion, optimizer,
                train_loader, batch_size, epochs)

            validation = ValidationKFold(
                model, criterion, validate_loader, batch_size, max_body_length)

            training.run(k_folds, fold, 2*len(consistent_json_dataset_), "fine_tuned_model", validation=validation)
            validation.save_data("fine_tuned_model")

            # all_predictions = validation.run(0.5, k, folds, store_all_predictions=True)
            # analyze_predictions(all_predictions, inconsistent_json_dataset, "human_labelled_model")