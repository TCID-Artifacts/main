from torch.utils.data import Dataset
import json


class JSONInMemoryDataset(Dataset):
    def __init__(self, json_files):
        self.items = []
        for f in json_files:
            with open(f) as fp:
                data = json.load(fp)
                self.items.extend(data)

    def __getitem__(self, idx):
        return self.items[idx]

    def __len__(self):
        return len(self.items)

        