import config
import torch
from dataset import get_dataloader
from model import ReviewAnalyzeModel
from predict import predict_batch
from tokenizer import JiebaTokenizer


def evaluate(model, test_dataloader, device):
    model.eval()  # 设置模型为评估模式
    total_count = 0
    correct_count = 0
    # 评估逻辑
    for inputs, targets in test_dataloader:
        inputs, targets = inputs.to(device), targets.to(device)
        target = targets.tolist()
        batch_result = predict_batch(model, inputs)
        # batch_result.shape = [batch_size]
        # target.shape = [batch_size]
        for result, target in zip(batch_result, target):  # 将预测结果和真实标签进行配对
            if result >= 0.5:
                result = 1
            elif result < 0.5 and result >= 0:
                result = 0

            total_count += 1
            if result == target:
                correct_count += 1

    accuracy = correct_count / total_count if total_count > 0 else 0
    return accuracy


def run_evaluate():
    # 确定设备
    device = "cuda" if torch.cuda.is_available() else "cpu"
    # 词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / "vocab.txt")
    # 模型
    model = ReviewAnalyzeModel(
        vocab_size=tokenizer.vocab_size, padding_index=tokenizer.pad_token_index
    ).to(device)
    model.load_state_dict(torch.load(config.MODELS_DIR / "model.pth"))
    print("模型加载成功！")

    # 数据集
    test_dataloader = get_dataloader(train=False)

    # 评估逻辑
    acc = evaluate(model, test_dataloader, device)
    print(f"准确率：{acc:.4f}")


if __name__ == "__main__":
    run_evaluate()
