import torch as t
import socket
from nltk.corpus import stopwords

# determines what datatype will be used in tensors
## dtype = t.float if t.cuda.is_available() else t.cuda.float
dtype = t.float

# determines which device will be used to store the tensor
# TODO: if we want to use GPU we need to refactor code to avoid
# loading too much data at once. But it is not that slow with CPU.
# The advantage of using CPU is that we can use the machine RAM,
# which typically much higher than GPU's memory size).
device = "cuda" if t.cuda.is_available() else "cpu"
# device = "cpu"

# determines how many tokens from the test body will be considered in the representation
max_body_length = 60

# preloads list of english stopwords
en_stops = set(stopwords.words('english'))

# size of batches of data (provided on input to the net)
batch_size = 100

# number of epochs
epochs = 10

# learning rate
lr = 1e-2

# number of groups to split the dataset
k_folds = 10