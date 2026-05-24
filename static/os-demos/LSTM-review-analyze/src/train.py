import time

import config
import torch
from dataset import get_dataloader
from model import ReviewAnalyzeModel
from tokenizer import JiebaTokenizer
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm


def train_one_epoch(model, dataloader, loss_fn, optimizer, device):
    total_loss = 0
    model.train()
    for inputs, targets in tqdm(dataloader, desc="Training"):
        inputs = inputs.to(device)  # inputs.shape = [batch_size, seq_len]
        targets = targets.to(device)  # targets.shape = [batch_size]
        output = model(inputs)
        loss = loss_fn(output, targets)

        loss.backward()
        optimizer.step()
        optimizer.zero_grad()
        total_loss += loss.item()
    return total_loss / len(dataloader)


def train():
    # 1.设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 2.数据
    dataloader = get_dataloader()
    # 3.分词器
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / "vocab.txt")
    # 4.模型
    model = ReviewAnalyzeModel(tokenizer.vocab_size, tokenizer.pad_token_index).to(
        device
    )
    # 5.损失函数
    loss_fn = torch.nn.BCEWithLogitsLoss()
    # 6.优化器
    optimizer = torch.optim.Adam(model.parameters(), lr=config.LEARNING_RATE)
    # 7.Tensorboard Writer
    writer = SummaryWriter(log_dir=config.LOGS_DIR / time.strftime("%Y-%m-%d-%H-%M-%S"))

    best_loss = float("inf")
    # 8.训练
    for epoch in range(1, config.EPOCHS + 1):
        print(f"========= Epoch {epoch} =========")
        loss = train_one_epoch(model, dataloader, loss_fn, optimizer, device)  # noqa: F821
        print(f"loss: {loss:.4f}")

        writer.add_scalar("loss", loss, epoch)  # 添加loss到Tensorboard

        # 保存模型
        if loss < best_loss:
            best_loss = loss
            torch.save(model.state_dict(), config.MODELS_DIR / "model.pth")
            print("模型已保存！")

    writer.close()


if __name__ == "__main__":
    train()
