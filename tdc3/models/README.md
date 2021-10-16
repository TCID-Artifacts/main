# Models

This directory contains the scripts to train and evaluate our models.

## Download Models

To use the models we trained and fine-tuned, run:

```bash
(tdc3) $> ./download_trained_models
```

## Steps to Reproduce

If you want to train, evaluate and fine-tune a model yourself (it can take hours), follow the instructions bellow:

1. Download the data:

```bash
(tdc3) $> cd ../data
(tdc3) $> ./download_data.sh
(tdc3) $> ./download_labeled_data.sh
(tdc3) $> cd ../models
```

2. Train and evaluate the model (Automatically labeled dataset):

```bash
(tdc3) $> ./train_eval.sh
```

3. Evaluate the model (Manually labeled dataset):

```bash
(tdc3) $> ./eval_on_human_labeled_data
```

4. Fine-tune and evaluate the model (Manually labeled dataset):

```bash
(tdc3) $> ./fine_tune_eval_k_fold
```

5. Train final model (Fine-tune with entire manually labeled dataset):

```bash
(tdc3) $> ./train_final_model
```

