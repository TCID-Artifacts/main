from torch.utils.data import IterableDataset
import json


class JSONOnDiskDataset(IterableDataset):
    def __init__(self, json_files):
        self.json_files = json_files

    def __iter__(self):
        for f in self.json_files:
            with open(f) as fp:
                data = json.load(fp)
                for item in data:
                    yield item
