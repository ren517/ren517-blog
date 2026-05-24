import config
import torch
from model import ReviewAnalyzeModel
from tokenizer import JiebaTokenizer


def predict_batch(model, input_tensor):
    model.eval()
    with torch.no_grad():
        outputs = model(input_tensor)
        # output.shape = [batch_size]
        outputs = torch.sigmoid(outputs)
        batch_result = outputs.cpu().numpy()
    return batch_result.tolist()


def predict(text, model, tokenizer, device):
    # 1.处理输入
    indexes = tokenizer.encode(text, config.SEQ_LEN)
    input_tensor = torch.tensor([indexes], dtype=torch.long)
    input_tensor = input_tensor.to(device)

    # 2.预测逻辑
    batch_result = predict_batch(model, input_tensor)

    return batch_result[0]


def run_predict():
    # 1.设备
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # 2.词表
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / "vocab.txt")
    print("词表加载成功")

    # 3.模型

    # 模型参数设置
    model = ReviewAnalyzeModel(tokenizer.vocab_size, tokenizer.pad_token_index).to(
        device
    )

    # 模型选择
    model.load_state_dict(
        torch.load(config.MODELS_DIR / "model.pth", map_location=device)
    )

    print("欢迎使用情感分析模型")

    while True:
        user_input = input(">")

        if user_input in ["q", "quit"]:
            print("退出程序")
            break

        if user_input.strip() == "":
            print("输入不能为空，请重新输入")
            continue

        result = predict(user_input, model, tokenizer, device)

        if result > 0.5:
            print("正向")
            print(f"概率: {result:.4f}")
        else:
            print("负向")
            print(f"概率: {1 - result:.4f}")


if __name__ == "__main__":
    run_predict()
