import numpy as np
import torch as t
from py.models.Validation import Validation
import matplotlib.pyplot as plt

class Training():

    def __init__(self, model, criterion, optimizer, data_loader, batch_size, epochs):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.data_loader = data_loader
        self.batch_size = batch_size
        self.epochs = epochs

    def run(self, store_model_path=None, validation=None, training_size=0.8, execution=1):
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

            if validation:
                if type(validation) is Validation:
                    thresholds = [0.5]
                    for threshold in thresholds:
                        validation.run(threshold=threshold, epoch=epoch, training_size=training_size, execution=execution)
                elif type(validation) is dict:
                    for name, validator in validation.items():
                        print(f"  Validation on {name}:")
                        validator.run()

            if store_model_path:
                t.save(self.model.state_dict(),
                       f"{store_model_path}_epoch{epoch}")

