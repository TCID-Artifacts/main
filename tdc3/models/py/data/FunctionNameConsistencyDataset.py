import random
import torch as t
from py.data.XYDataset import XYDataset
from py.util.Config import dtype, device, en_stops
from nltk.tokenize import word_tokenize
import numpy as np

def genericDescriptionClassifier(description, embedding):
    some_generic_descriptions = ['work', 'success', 'test', 'filter',
                                 'failure', 'explodes', 'case', 'scenario', 'screen']
    for generic_description in some_generic_descriptions:
        if embedding.similarity(generic_description, description) > 0.5:
            return True
    return False

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

    def similarity(self, token, comparison_token):
        return self.embedding.similarity(token, comparison_token)


class FunctionNameConsistencyDataset(XYDataset):
    def __init__(self, description_embedding, test_embedding, embedding_size, max_body_length, max_description_length):
        self.description_embedding = description_embedding
        self.test_embedding = test_embedding
        self.embedding_size = embedding_size
        self.max_body_length = max_body_length
        self.max_description_length = max_description_length

    def prepare_data(self, json_dataset):
        print("Preparing dataset")
        self.body_tensors = []
        self.description_tensors = []
        self.is_consistent_tensors = []  # consistent (1.0) inconsistent (0.0)
        self.ids = [] # unique id for each item, useful for debugging

        de = Embedding(self.description_embedding)
        te = Embedding(self.test_embedding)

        # read all data once to get test descriptions embeddings for creating negative examples
        print(f"Reading all data once to get all test descriptions")
        description_vectors = []
        for token_seq in json_dataset:
            test_description = token_seq["metadata"]["description"]
            description_vec = []
            for token in word_tokenize(test_description)[:self.max_description_length]:
                if token not in en_stops:
                    description_vec.append(de.get(token))
            while len(description_vec) < self.max_description_length:
                description_vec.append([0] * self.embedding_size)
            description_vectors.append(description_vec)

        # read all data again to create positive and negative examples
        print(f"Creating positive and negative examples")
        next_neg_example_id = -1 # negative ids for negative examples
        for idx in range(len(json_dataset)):
            token_seq = json_dataset[idx]
            description_vec = description_vectors[idx]

            body_vec = []
            for token in token_seq["data"][:self.max_body_length]:
                if token not in en_stops:
                    body_vec.append(te.get(token))
            while len(body_vec) < self.max_body_length:
                body_vec.append([0] * self.embedding_size)

            # positive example
            self.body_tensors.append(body_vec)
            self.description_tensors.append(description_vec)
            self.is_consistent_tensors.append([1.0])
            self.ids.append(token_seq["id"])

            # negative example (randomly combine a description with a test body)
            some_other_description_vec = random.choice(description_vectors)
            self.body_tensors.append(body_vec)
            self.description_tensors.append(some_other_description_vec)
            self.is_consistent_tensors.append([0.0])
            self.ids.append(next_neg_example_id)
            next_neg_example_id -= 1

            if len(self.body_tensors) % 1000 == 0:
                print(
                    f"Have created {len(self.body_tensors)}/{2*len(description_vectors)} data points")

            if len(self.body_tensors) % 1000 == 0:
                print(
                    f"Have created {len(self.body_tensors)}/{2*len(description_vectors)} data points")

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


class ToyDataset(XYDataset):
    def __init__(self, nb_datapoints, embedding_size, seq_length):
        self.embedding_size = embedding_size
        self.body_tensors = t.empty(
            nb_datapoints, seq_length, embedding_size, dtype=dtype, device=device)
        self.description_tensors = t.empty(
            nb_datapoints, embedding_size, dtype=dtype, device=device)
        self.is_consistent_tensors = t.empty(
            nb_datapoints, 1, dtype=dtype, device=device)

        for datapoint_idx in range(nb_datapoints):
            token_vec1 = t.rand(embedding_size, dtype=dtype, device=device)
            token_vec2 = t.rand(embedding_size, dtype=dtype, device=device)
            token_vec3 = t.rand(embedding_size, dtype=dtype, device=device)
            if datapoint_idx % 2 == 0:
                for seq_idx in range(seq_length):
                    self.body_tensors[datapoint_idx][seq_idx] = token_vec1
                self.description_tensors[datapoint_idx] = token_vec1
                self.is_consistent_tensors[datapoint_idx] = 1.0
            else:
                for seq_idx in range(seq_length):
                    self.body_tensors[datapoint_idx][seq_idx] = token_vec2
                self.description_tensors[datapoint_idx] = token_vec3
                self.is_consistent_tensors[datapoint_idx] = 0.0

    def __len__(self):
        return len(self.body_tensors)

    def __getitem__(self, i):
        return [self.body_tensors[i], self.description_tensors[i]], self.is_consistent_tensors[i]
