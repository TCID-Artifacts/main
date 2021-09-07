import torch.nn as nn
import torch as t
import torch.nn.functional as F
import math


class TransformerModel(nn.Module):
    def __init__(self, embedding_size):
        super(TransformerModel, self).__init__()

        seq_summary_size = 100
        description_summary_size = 50
        joint_size = 200
        self.embedding_size = embedding_size

        # encode token sequence with transformer + LSTM
        self.pos_encoder = PositionalEncoding(d_model=embedding_size)
        self.encoder_layer = nn.TransformerEncoderLayer(batch_first=True,
                                                        d_model=embedding_size, nhead=2, dim_feedforward=200)
        self.transformer_encoder = nn.TransformerEncoder(
            self.encoder_layer, num_layers=1)
        self.lstm = nn.LSTM(input_size=embedding_size,
                            hidden_size=seq_summary_size, batch_first=True, bidirectional=True, num_layers=2, dropout=0.2)

        # encode description with LSTM
        self.description_lstm = nn.LSTM(input_size=embedding_size,
                            hidden_size=description_summary_size, batch_first=True, bidirectional=True, num_layers=2, dropout=0.2)
        
        # join encoding of tokens and description, and then predict if consistent
        self.joining_layer = nn.Linear(
            in_features=2*seq_summary_size + 2*description_summary_size, out_features=joint_size)
        self.final_fc = nn.Linear(in_features=joint_size, out_features=1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, xs):
        xs_body, xs_description = xs
        
        pos_encoded_body = self.pos_encoder(xs_body)
        trans_encoded_body = self.transformer_encoder(pos_encoded_body)
        lstm_out, _ = self.lstm(trans_encoded_body)
        body_summary = lstm_out.select(1, -1)
        
        description_lstm_out, _ = self.description_lstm(xs_description)
        description_summary = description_lstm_out.select(1, -1)
        
        joint_summaries = F.relu(self.joining_layer(
            t.cat((body_summary, description_summary), dim=1)))
        final_fc_out = self.final_fc(joint_summaries)
        prediction = self.sigmoid(final_fc_out)
        return prediction.view(len(prediction), 1)


class PositionalEncoding(nn.Module):

    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = t.zeros(max_len, d_model)
        position = t.arange(0, max_len, dtype=t.float).unsqueeze(1)
        div_term = t.exp(t.arange(0, d_model, 2).float()
                         * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = t.sin(position * div_term)
        pe[:, 1::2] = t.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)
