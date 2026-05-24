import config
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset


class ReviewAnalyzeDataset(Dataset):
    def __init__(self, path):
        self.data = pd.read_json(path, lines=True, orient="records").to_dict(
            orient="records"
        )  # data设置为字典类型

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        input_tensor = torch.tensor(self.data[index]["review"], dtype=torch.long)
        # BCEWithLogitsLoss 需要标签为 float 类型
        target_tensor = torch.tensor(self.data[index]["label"], dtype=torch.float)
        return input_tensor, target_tensor


def get_dataloader(train=True):
    path = config.PROCESSED_DATA_DIR / ("train.jsonl" if train else "test.jsonl")
    dataset = ReviewAnalyzeDataset(path)
    return DataLoader(dataset, batch_size=config.BATCH_SIZE, shuffle=True)


if __name__ == "__main__":
    train_dataloader = get_dataloader(train=True)
    test_dataloader = get_dataloader(train=False)
    print(len(train_dataloader))
    print(len(test_dataloader))

    for input_tensor, target_tensor in train_dataloader:
        print(input_tensor.shape)
        print(target_tensor.shape)
        break
