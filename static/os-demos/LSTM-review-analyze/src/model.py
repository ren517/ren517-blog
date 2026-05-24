import config
import torch
from torch import nn


class ReviewAnalyzeModel(nn.Module):
    def __init__(self, vocab_size, padding_index):
        super(ReviewAnalyzeModel, self).__init__()
        self.embedding = nn.Embedding(
            vocab_size, config.EMBEDDING_DIM, padding_idx=padding_index
        )
        self.lstm = nn.LSTM(
            input_size=config.EMBEDDING_DIM,
            hidden_size=config.HIDDEN_SIZE,
            batch_first=True,
        )
        self.linear = nn.Linear(config.HIDDEN_SIZE, 1)

    def forward(self, x):
        # x.shape = [batch_size, seq_len]
        embed = self.embedding(x)
        # embed.shape = [batch_size, seq_len, embedding_dim]
        output, (_, _) = self.lstm(embed)
        # output.shape = [batch_size, seq_len, hidden_size]

        # 取出最后一个时间步的隐藏状态
        batch_indexs = torch.arange(0, output.shape[0])
        # output = output[:, -1, :] # 由于x中第二维有很多0填充，需要改善
        lengths = (x != self.embedding.padding_idx).sum(
            dim=1
        ) - 1  # 计算每个样本的实际长度，减去1得到最后一个非0位置的索引
        last_hidden = output[batch_indexs, lengths]
        # last_hidden.shape = [batch_size, hidden_size]
        output = self.linear(last_hidden)
        return output.squeeze(-1)  # output.shape = [batch_size]
