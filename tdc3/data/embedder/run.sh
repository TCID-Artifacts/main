#!/bin/bash

mkdir ../embedded
cd ../embedded && mkdir description && mkdir test && cd ../embedder
python3 TokenEmbeddingLearner.py --tokens ../tokenized/*.json --descriptionmodelfile ../embedded/description/embeddingModel --testmodelfile ../embedded/test/embeddingModel