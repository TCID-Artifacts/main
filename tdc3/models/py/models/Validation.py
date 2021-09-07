import torch as t
from sklearn.metrics import precision_score, recall_score
import numpy as np
import matplotlib.pyplot as plt
import csv
import pandas as pd
import os

class Validation():

    def __init__(self, model, criterion, data_loader, batch_size, max_body_length):
        self.model = model
        self.criterion = criterion
        self.data_loader = data_loader
        self.batch_size = batch_size
        self.max_body_length = max_body_length
        # for plotting
        self.val_accuracy_at_epoch = []
        self.val_loss_at_epoch = []
        self.val_precision_at_inconsistent_at_epoch = []
        self.val_recall_at_inconsistent_at_epoch = []
        self.val_f1_at_inconsistent_at_epoch = []
        self.val_threshold_at_epoch = []
        self.val_training_size_at_epoch = []
        self.val_execution_at_epoch = []
        self.val_epoch = []

    def run(self, threshold, epoch, training_size=0.8, execution=1, store_all_predictions=False):
        considered_cases = 0
        correct_predictions = 0
        losses = 0

        correct_inconsistent_predictions = 0
        total_inconsistent_labels = 0
        total_inconsistent_predictions = 0

        all_predictions = []

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

                        if pred < threshold and label == 0.0:
                            correct_predictions += 1
                            correct_inconsistent_predictions += 1
                        elif pred > (1 - threshold) and label == 1.0:
                            correct_predictions += 1

                        # Use this to debug individual data points:
                        # print(f"Made prediction for pair with id {ids[i]}")

                    if store_all_predictions:
                        all_predictions.append([ids[i].item(), label.item(), pred.item()])
                        #all_predictions.append(pred.item())

        val_accuracy = correct_predictions/considered_cases if considered_cases > 0 else 0
        val_loss = losses/considered_cases if considered_cases > 0 else float("inf")
        val_precision_at_inconsistent = correct_inconsistent_predictions/total_inconsistent_predictions if total_inconsistent_predictions > 0 else 0
        val_recall_at_inconsistent = correct_inconsistent_predictions/total_inconsistent_labels if total_inconsistent_labels > 0 else 0
        val_f1_at_inconsistent = 2 * ((val_precision_at_inconsistent * val_recall_at_inconsistent)/(val_precision_at_inconsistent + val_recall_at_inconsistent)) if (val_precision_at_inconsistent + val_recall_at_inconsistent) > 0 else 0

        print("================================================================================")
        print("results from validation.run():")
        print(
            f"val_loss = {round(val_loss, 4)}, val_accuracy = {round(val_accuracy, 4)}")
        print(
            f"val_precision@I = {round(val_precision_at_inconsistent, 4)}, val_recall@I = {round(val_recall_at_inconsistent, 4)}")
        print(
            f"val_F1@I = {round(val_f1_at_inconsistent, 4)}")

        # update list of measurements for plotting
        self.val_accuracy_at_epoch.append(val_accuracy)
        self.val_loss_at_epoch.append(val_loss)
        self.val_precision_at_inconsistent_at_epoch.append(val_precision_at_inconsistent)
        self.val_recall_at_inconsistent_at_epoch.append(val_recall_at_inconsistent)
        self.val_f1_at_inconsistent_at_epoch.append(val_f1_at_inconsistent)
        self.val_threshold_at_epoch.append(threshold)
        self.val_training_size_at_epoch.append(training_size)
        self.val_execution_at_epoch.append(execution)
        self.val_epoch.append(epoch)

        return all_predictions

    def save_data(self):
        dataframe = pd.DataFrame({
            'loss': self.val_loss_at_epoch,
            'accuracy': self.val_accuracy_at_epoch,
            'precision_at_inconsistent': self.val_precision_at_inconsistent_at_epoch,
            'recall_at_inconsistent': self.val_recall_at_inconsistent_at_epoch,
            'f1_at_inconsistent': self.val_f1_at_inconsistent_at_epoch,
            'threshold': self.val_threshold_at_epoch
            })
        dataframe.to_csv('metrics_n_' + str(self.max_body_length) + '.csv', index=False)

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

    def plot(self, model, data_loader):
        print("generating plots...")
        print(self.val_loss_at_epoch)
        ## losses.png
        numpoints = len(self.val_accuracy_at_epoch)
        line_losses, = plt.plot(np.linspace(1, numpoints, numpoints).astype(int), self.val_loss_at_epoch)
        plt.xlabel("epoch")
        plt.ylabel("losses")
        plt.savefig("loss.png")
        plt.clf()

        ## accuracy.png
        line_accuracies, = plt.plot(np.linspace(1, numpoints, numpoints).astype(int), self.val_accuracy_at_epoch)
        plt.xlabel("epoch")
        plt.ylabel("accuracy")
        plt.savefig("accuracy.png")
        plt.clf()

        ## recall_at_inconsistent.png
        line_recalls_at_inconsistent, = plt.plot(np.linspace(1, numpoints, numpoints).astype(int), self.val_recall_at_inconsistent_at_epoch)
        plt.xlabel("epoch")
        plt.ylabel("recall@inconsistent")
        plt.savefig("recall_at_inconsistent.png")
        plt.clf()

        # prediction distribution (histogram)
        positive_labels_predictions = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        negative_labels_predictions = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}

        with t.no_grad():
            model.eval()
            for batch_idx, batch in enumerate(data_loader):
                xs = batch[0]
                ys = batch[1]
                ys_pred = model(xs)
                for i in range(len(ys_pred.cpu().numpy())):
                    pred = ys_pred.cpu().numpy()[i][0]
                    label = ys.cpu().numpy()[i][0]

                    if label == 1.0:
                        if (pred < 0.1):
                            positive_labels_predictions[0] += 1
                        elif (pred >= 0.1 and pred < 0.2):
                            positive_labels_predictions[1] += 1
                        elif (pred >= 0.2 and pred < 0.3):
                            positive_labels_predictions[2] += 1
                        elif (pred >= 0.3 and pred < 0.4):
                            positive_labels_predictions[3] += 1
                        elif (pred >= 0.4 and pred < 0.5):
                            positive_labels_predictions[4] += 1
                        elif (pred >= 0.5 and pred < 0.6):
                            positive_labels_predictions[5] += 1
                        elif (pred >= 0.6 and pred < 0.7):
                            positive_labels_predictions[6] += 1
                        elif (pred >= 0.7 and pred < 0.8):
                            positive_labels_predictions[7] += 1
                        elif (pred >= 0.8 and pred < 0.9):
                            positive_labels_predictions[8] += 1
                        elif (pred >= 0.9):
                            positive_labels_predictions[9] += 1
                    else:
                        if (pred < 0.1):
                            negative_labels_predictions[0] += 1
                        elif (pred >= 0.1 and pred < 0.2):
                            negative_labels_predictions[1] += 1
                        elif (pred >= 0.2 and pred < 0.3):
                            negative_labels_predictions[2] += 1
                        elif (pred >= 0.3 and pred < 0.4):
                            negative_labels_predictions[3] += 1
                        elif (pred >= 0.4 and pred < 0.5):
                            negative_labels_predictions[4] += 1
                        elif (pred >= 0.5 and pred < 0.6):
                            negative_labels_predictions[5] += 1
                        elif (pred >= 0.6 and pred < 0.7):
                            negative_labels_predictions[6] += 1
                        elif (pred >= 0.7 and pred < 0.8):
                            negative_labels_predictions[7] += 1
                        elif (pred >= 0.8 and pred < 0.9):
                            negative_labels_predictions[8] += 1
                        elif (pred >= 0.9):
                            negative_labels_predictions[9] += 1

        plt.figure(figsize=(6, 4))

        series_labels = ['Consistent', 'Inconsistent']

        data = [
           list(positive_labels_predictions.values()),
           list(negative_labels_predictions.values())
        ]

        category_labels = [x / 10 for x in positive_labels_predictions.keys()]

        self.plot_stacked_bar(
            data, 
            series_labels, 
            category_labels=category_labels, 
            show_values=True, 
            value_format="{:.2f}",
            colors=[str((255 - 27)/255), str((255 - 220)/255)]
        )

        plt.savefig('bar.png')

    def plot_stacked_bar(self, data, series_labels, category_labels=None, 
                     show_values=False, value_format="{}", y_label=None, 
                     colors=None, grid=False, reverse=False):
        ny = len(data[0])
        ind = list(range(ny))

        axes = []
        cum_size = np.zeros(ny)

        data = np.array(data)

        if reverse:
            data = np.flip(data, axis=1)
            category_labels = reversed(category_labels)

        for i, row_data in enumerate(data):
            color = colors[i] if colors is not None else None
            axes.append(plt.bar(ind, row_data, bottom=cum_size, 
                                label=series_labels[i], color=color))
            cum_size += row_data

        if category_labels:
            plt.xticks(ind, category_labels)

        if y_label:
            plt.ylabel(y_label)

        plt.legend()

        if grid:
            plt.grid()

   