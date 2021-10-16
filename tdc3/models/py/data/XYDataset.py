import torch as t
from torch.utils.data import Dataset


class XYDataset(Dataset):
    '''
    Base class for datasets that consist of (x, y) pairs,
    where x typically is the input to a model
    and y typically is the prediction of a model.
    '''

    
