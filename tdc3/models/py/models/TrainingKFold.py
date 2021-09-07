import numpy as np
import torch as t
from py.models.ValidationKFold import ValidationKFold
import matplotlib.pyplot as plt

class TrainingKFold():

    def __init__(self, model, criterion, optimizer, data_loader, batch_size, epochs):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.data_loader = data_loader
        self.batch_size = batch_size
        self.epochs = epochs

    def run(self, k, fold, dataset_size, store_model_path=None, validation=None):
        print("Starting training")
        for epoch in range(self.epochs):
            print(f"Epoch {epoch}")
            self.model.train()
            batch_losses = []
            for batch_idx, batch in enumerate(self.data_loader):
                xs = batch[0]
                ys = batch[1]

                self.optimizer.zero_grad()
                ys_pred = self.model(xs)
                loss = self.criterion(ys_pred, ys)
                loss.backward()
                self.optimizer.step()

                if batch_idx % 100 == 0:
                    print(
                        f"  Training loss of batch {batch_idx}: {round(loss.item(), 4)}")

                batch_losses.append(loss.item())
            print('Training process has finished.')

        if validation:
            if type(validation) is ValidationKFold:
                thresholds = [0.5, 0.3, 0.1]
                for threshold in thresholds:
                    validation.run(threshold, k, fold, dataset_size)
            elif type(validation) is dict:
                for name, validator in validation.items():
                    print(f"  Validation on {name}:")
                    validator.run()

        if store_model_path:
            t.save(self.model.state_dict(),
                f"{store_model_path}_{k}_folds_fold_{fold}")

