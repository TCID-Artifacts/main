import torch.nn as nn
import torch as t
import torch.nn.functional as F


class FunctionNameConsistencyModel(nn.Module):
    def __init__(self, embedding_size):
        super(FunctionNameConsistencyModel, self).__init__()

        body_summary_size = 100
        description_summary_size = 50
        joint_size = 200
        self.embedding_size = embedding_size
        self.body_lstm = nn.LSTM(input_size=embedding_size,
                            hidden_size=body_summary_size, batch_first=True, bidirectional=True, num_layers=2, dropout=0.2)
        self.description_lstm = nn.LSTM(input_size=embedding_size,
                            hidden_size=description_summary_size, batch_first=True, bidirectional=True, num_layers=2, dropout=0.2)
        self.joining_layer = nn.Linear(
            in_features=2*body_summary_size + 2*description_summary_size, out_features=joint_size)
        self.final_fc = nn.Linear(in_features=joint_size, out_features=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, xs):
        xs_body, xs_description = xs
        body_lstm_out, _ = self.body_lstm(xs_body)
        body_summary = body_lstm_out.select(1, -1)
        description_lstm_out, _ = self.description_lstm(xs_description)
        description_summary = description_lstm_out.select(1, -1)
        joint_summaries = F.relu(self.joining_layer(
            t.cat((body_summary, description_summary), dim=1)))
        final_fc_out = self.final_fc(joint_summaries)
        prediction = self.sigmoid(final_fc_out)
        return prediction.view(len(prediction), 1)
