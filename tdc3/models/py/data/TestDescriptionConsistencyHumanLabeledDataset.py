import random
import torch as t
from py.data.XYDataset import XYDataset
from py.util.Config import dtype, device
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import numpy as np

en_stops = set(stopwords.words('english'))

# TODO: move into more reusable class
class Embedding():
    def __init__(self, embedding):
        self.embedding = embedding
        self.cache = {}

    def get(self, token):
        if token in self.cache:
            return self.cache[token]
        else:
            vec = self.embedding[token]
            self.cache[token] = vec 
            return vec


class TestDescriptionConsistencyHumanLabeledDataset(XYDataset):
    def __init__(self, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length):
        self.description_embedding = description_embedding
        self.test_embedding = test_embedding
        self.embedding_size = embedding_size
        self.max_body_length = max_body_length
        self.max_description_length = max_description_length

    def prepare_data(self, consistent_json_dataset, inconsistent_json_dataset):
        print("Preparing dataset")
        self.body_tensors = []
        self.description_tensors = []
        self.is_consistent_tensors = []  # consistent (1.0) inconsistent (0.0)
        self.ids = [] # unique id for each item, useful for debugging

        de = Embedding(self.description_embedding)
        te = Embedding(self.test_embedding)

        # add human labelled data
        # positive examples
        for token_seq in consistent_json_dataset:
            test_description = token_seq["metadata"]["description"]
            description_vec = []
            for token in word_tokenize(test_description)[:self.max_description_length]:
                if token not in en_stops:
                    description_vec.append(de.get(token))
            while len(description_vec) < self.max_description_length:
                description_vec.append([0] * self.embedding_size)

            body_vec = []
            for token in token_seq["data"][:self.max_body_length]:
                if token not in en_stops:
                    body_vec.append(te.get(token))
            while len(body_vec) < self.max_body_length:
                body_vec.append([0] * self.embedding_size)

            self.body_tensors.append(body_vec)
            self.description_tensors.append(description_vec)
            self.is_consistent_tensors.append([1.0])
            self.ids.append(token_seq["id"])

        # negative examples
        next_neg_example_id = -1 # negative ids for for negative examples
        for token_seq in inconsistent_json_dataset:
            test_description = token_seq["metadata"]["description"]
            description_vec = []
            for token in word_tokenize(test_description)[:self.max_description_length]:
                if token not in en_stops:
                    description_vec.append(de.get(token))
            while len(description_vec) < self.max_description_length:
                description_vec.append([0] * self.embedding_size)

            body_vec = []
            for token in token_seq["data"][:self.max_body_length]:
                if token not in en_stops:
                    body_vec.append(te.get(token))
            while len(body_vec) < self.max_body_length:
                body_vec.append([0] * self.embedding_size)

            self.body_tensors.append(body_vec)
            self.description_tensors.append(description_vec)
            self.is_consistent_tensors.append([0.0])
            self.ids.append(next_neg_example_id)
            next_neg_example_id -= 1

        self.body_tensors = t.as_tensor(
            self.body_tensors, dtype=dtype, device="cpu")
        self.description_tensors = t.as_tensor(
            self.description_tensors, dtype=dtype, device="cpu")
        self.is_consistent_tensors = t.as_tensor(
            self.is_consistent_tensors, dtype=dtype, device="cpu")
        self.ids = t.as_tensor(
            self.ids, device="cpu")
        print(
            f"Done with data preparation: {len(self.body_tensors)} datapoints")

    def save_to_disk(self, filename):
        t.save({"body_tensors": self.body_tensors,
                "description_tensors": self.description_tensors,
                "is_consistent_tensors": self.is_consistent_tensors,
                "ids": self.ids},
               filename)

    def load_from_disk(self, filename):
        tensors = t.load(filename)
        self.body_tensors = tensors["body_tensors"]
        self.description_tensors = tensors["description_tensors"]
        self.is_consistent_tensors = tensors["is_consistent_tensors"]
        self.ids = tensors["ids"]

    def move_to_target_device(self):
        print("Moving dataset to target device (e.g. GPU)")
        self.body_tensors = t.as_tensor(
            self.body_tensors, dtype=dtype, device=device)
        self.description_tensors = t.as_tensor(
            self.description_tensors, dtype=dtype, device=device)
        self.is_consistent_tensors = t.as_tensor(
            self.is_consistent_tensors, dtype=dtype, device=device)
        self.ids = t.as_tensor(
                self.ids, dtype=dtype, device=device)

    def __len__(self):
        return len(self.body_tensors)

    def __getitem__(self, index):
        return [self.body_tensors[index], self.description_tensors[index]], self.is_consistent_tensors[index], self.ids[index]

