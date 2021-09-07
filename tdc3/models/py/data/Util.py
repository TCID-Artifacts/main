from os import listdir
from os.path import isfile, join
from torch.utils.data import random_split


def json_files_in_dir(dir):
    return [join(dir, f) for f in listdir(
        dir) if isfile(join(dir, f)) and f.endswith(".json")]


def split_dataset(dataset, train_perc):
    print("Splitting data into training and validation sets")
    train_size = int(train_perc*len(dataset))
    validate_size = len(dataset) - train_size
    train_dataset, validate_dataset = random_split(
        dataset, lengths=[train_size, validate_size])
    print(f"{len(train_dataset)} training samples, {len(validate_dataset)} validation samples")
    return train_dataset, validate_dataset
