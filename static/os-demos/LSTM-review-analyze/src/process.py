import config
import pandas as pd
from sklearn.model_selection import train_test_split
from tokenizer import JiebaTokenizer


def process():
    print("开始处理数据")
    df = (
        pd.read_csv(
            config.RAW_DATA_DIR / "online_shopping_10_cats.csv",
            usecols=["label", "review"],
            encoding="utf-8",
        )
        .dropna()  # 删除DataFrame中包含缺失值的行或列
        .sample(frac=1)  # 取100%数据
    )

    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df["label"])

    # 构建词表
    JiebaTokenizer.build_vocab(
        (train_df["review"].tolist()), vocab_path=config.MODELS_DIR / "vocab.txt"
    )

    # 创建tokenizer
    tokenizer = JiebaTokenizer.from_vocab(config.MODELS_DIR / "vocab.txt")

    # 计算序列长度
    # max_len = train_df["review"].apply(lambda x: len(tokenizer.tokenize((x)))).quantile(0.95) # 取整为128
    # 编码训练集
    train_df["review"] = train_df["review"].apply(lambda x: tokenizer.encode(x, 128))

    # 导出训练集
    train_df.to_json(
        config.PROCESSED_DATA_DIR / "train.jsonl",
        orient="records",
        lines=True,
    )

    # 编码测试集
    test_df["review"] = test_df["review"].apply(lambda x: tokenizer.encode(x, 128))
    # 导出测试集
    test_df.to_json(
        config.PROCESSED_DATA_DIR / "test.jsonl",
        orient="records",
        lines=True,
    )

    print("数据处理完成")


if __name__ == "__main__":
    process()
