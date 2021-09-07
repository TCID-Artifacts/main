import torch as t
from sklearn.metrics import precision_score, recall_score
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import os

class ValidationKFold():

    def __init__(self, model, criterion, data_loader, batch_size, max_body_length):
        self.model = model
        self.criterion = criterion
        self.data_loader = data_loader
        self.batch_size = batch_size
        self.max_body_length = max_body_length
        # for plotting
        self.val_accuracy_at_fold = []
        self.val_loss_at_fold = []
        self.val_precision_at_inconsistent_at_fold = []
        self.val_recall_at_inconsistent_at_fold = []
        self.val_f1_at_inconsistent_at_epoch = []
        self.val_threshold_at_fold = []
        self.val_k = []
        self.val_fold = []
        self.val_dataset_size = []

    def run(self, threshold, k, fold, dataset_size, store_all_predictions=False):
        considered_cases = 0
        correct_predictions = 0
        losses = 0

        correct_inconsistent_predictions = 0
        total_inconsistent_labels = 0
        total_inconsistent_predictions = 0

        all_predictions = []

        print("Starting validation")
        with t.no_grad():
            self.model.eval()
            for batch_idx, batch in enumerate(self.data_loader):
                xs = batch[0]
                ys = batch[1]
                ids = batch[2]

                ys_pred = self.model(xs)

                for i in range(len(ys_pred.cpu().numpy())):
                    pred = ys_pred.cpu().numpy()[i][0]
                    label = ys.cpu().numpy()[i][0]

                    if label == 0.0:
                        total_inconsistent_labels += 1
                    if pred < threshold:
                        total_inconsistent_predictions += 1

                    if pred < threshold or pred > (1 - threshold):
                        considered_cases += 1 
                        losses += abs(label - pred)

                        if pred <= threshold and label == 0.0:
                            correct_predictions += 1
                            correct_inconsistent_predictions += 1
                        elif pred >= (1 - threshold) and label == 1.0:
                            correct_predictions += 1

                        # Use this to debug individual data points:
                        # print(f"Made prediction for pair with id {ids[i]}")

                    if store_all_predictions:
                        all_predictions.append([ids[i].item(), label.item(), pred.item()])
                        #all_predictions.append(pred.item())

        print("Validation process has finished.")

        val_accuracy = correct_predictions/considered_cases if considered_cases > 0 else 0
        val_loss = losses/considered_cases if considered_cases > 0 else float("inf")
        val_precision_at_inconsistent = correct_inconsistent_predictions/total_inconsistent_predictions if total_inconsistent_predictions > 0 else 0
        val_recall_at_inconsistent = correct_inconsistent_predictions/total_inconsistent_labels if total_inconsistent_labels > 0 else 0
        val_f1_at_inconsistent = 2 * ((val_precision_at_inconsistent * val_recall_at_inconsistent)/(val_precision_at_inconsistent + val_recall_at_inconsistent))

        print("================================================================================")
        print(f"results for fold {fold + 1} out ({k}-folds):")
        print(
            f"val_loss = {round(val_loss, 4)}, val_accuracy = {round(val_accuracy, 4)}")
        print(
            f"val_precision@I = {round(val_precision_at_inconsistent, 4)}, val_recall@I = {round(val_recall_at_inconsistent, 4)}")
        print(
            f"val_F1@I = {round(val_f1_at_inconsistent, 4)}")

        # update list of measurements for plotting
        self.val_accuracy_at_fold.append(val_accuracy)
        self.val_loss_at_fold.append(val_loss)
        self.val_precision_at_inconsistent_at_fold.append(val_precision_at_inconsistent)
        self.val_recall_at_inconsistent_at_fold.append(val_recall_at_inconsistent)
        self.val_f1_at_inconsistent_at_epoch.append(val_f1_at_inconsistent)
        self.val_threshold_at_fold.append(threshold)
        self.val_k.append(k)
        self.val_fold.append(fold + 1)
        self.val_dataset_size.append(dataset_size)

        return all_predictions

    def save_data(self, model_type):
        # Create CSV file and add header if it doesn't exist 
        if not os.path.isfile(f'./data_{model_type}.csv'):
            columns = ['loss', 'accuracy', 'precision_at_inconsistent', 'recall_at_inconsistent', 'f1_at_inconsistent', 'threshold', 'k', 'fold', 'dataset_size']

            with open(f'./data_{model_type}.csv', 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(columns)
                
        df = pd.read_csv(f'./data_{model_type}.csv')
        df_new_data = pd.DataFrame({
            'loss': self.val_loss_at_fold,
            'accuracy': self.val_accuracy_at_fold,
            'precision_at_inconsistent': self.val_precision_at_inconsistent_at_fold,
            'recall_at_inconsistent': self.val_recall_at_inconsistent_at_fold,
            'f1_at_inconsistent': self.val_f1_at_inconsistent_at_epoch,
            'threshold': self.val_threshold_at_fold,
            'k': self.val_k,
            'fold': self.val_fold,
            'dataset_size': self.val_dataset_size
            })
        df = df.append(df_new_data)
        df.to_csv(f'./data_{model_type}.csv', index=False)

    def save_experimental_data(self, model_type):
        # Create CSV file and add header if it doesn't exist 
        if not os.path.isfile(f'./experimental_data_{model_type}.csv'):
            columns = ['loss', 'accuracy', 'precision_at_inconsistent', 'recall_at_inconsistent', 'f1_at_inconsistent', 'training_size', 'execution', 'epoch']

            with open(f'./experimental_data_{model_type}.csv', 'a') as csvFile:
                writer = csv.writer(csvFile)
                writer.writerow(columns)

        df = pd.read_csv(f'./experimental_data_{model_type}.csv')
        df_new_data = pd.DataFrame({
            'loss': self.val_loss_at_epoch,
            'accuracy': self.val_accuracy_at_epoch,
            'precision_at_inconsistent': self.val_precision_at_inconsistent_at_epoch,
            'recall_at_inconsistent': self.val_recall_at_inconsistent_at_epoch,
            'f1_at_inconsistent': self.val_f1_at_inconsistent_at_epoch,
            'training_size': self.val_training_size_at_epoch,
            'execution': self.val_execution_at_epoch,
            'epoch': self.val_epoch
            })
        df = df.append(df_new_data)
        df.to_csv(f'./experimental_data_{model_type}.csv', index=False)

