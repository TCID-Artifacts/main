## Use TDC3

To use the model we trained and fine-tuned to check conformance of test-description pairs, run:

```bash
(tdc3) $> cd ./data && ./download_data.sh && cd ..
(tdc3) $> cd ./models
(tdc3) $> ./download_trained_models
(tdc3) $> ./mkdir input
```

Inside the input folder, create a CSV file containing the columns Description and Test. Then, insert the test-description pairs that you want to check conformance.

Finally, run:

```bash
(tdc3) $> cd ./tdc3
```

The predictions made by TDC3 for each given test-description pair must be on a column called TDC3Prediction of the CSV in the input folder. Lower predictions mean that the test description and the test are inconsistent.

## Reproduce TDC3

If you want to prepare the dataset, train, evaluate and fine-tune a model yourself, follow the instructions in the data and models folders.


