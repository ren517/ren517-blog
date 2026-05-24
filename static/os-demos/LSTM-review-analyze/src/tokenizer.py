import jieba
from tqdm import tqdm


class JiebaTokenizer:
    unk_token = "<unk>"
    pad_token = "<pad>"

    def __init__(self, vocab_list):
        self.vocab_list = vocab_list
        self.vocab_size = len(vocab_list)
        self.word2index = {word: index for index, word in enumerate(vocab_list)}
        self.index2word = {index: word for index, word in enumerate(vocab_list)}
        self.unk_token_index = self.word2index[self.unk_token]
        self.pad_token_index = self.word2index[self.pad_token]

    @staticmethod
    def tokenize(text):
        return jieba.lcut(text)

    def encode(self, text, seq_len):
        tokens = self.tokenize(text)
        # 截取或填充
        if len(tokens) > seq_len:
            tokens = tokens[:seq_len]
        elif len(tokens) < seq_len:
            tokens += [self.pad_token] * (seq_len - len(tokens))

        return [self.word2index.get(token, self.unk_token_index) for token in tokens]

    @classmethod
    def build_vocab(cls, sentences, vocab_path):
        vocab_set = set()
        for sentence in tqdm(sentences, desc="构建词表"):
            vocab_set.update(jieba.lcut(sentence))

        vocab_list = [cls.pad_token, cls.unk_token] + [
            token for token in vocab_set if token.strip() != ""
        ]
        print(f"词表大小:{len(vocab_list)}")

        # 保存词表
        with open(vocab_path, "w", encoding="utf-8") as f:
            f.write("\n".join(vocab_list))

        return cls(vocab_list)

    @classmethod
    def from_vocab(cls, vocab_path):
        """
        从文件加载词汇表并创建 Tokenizer 实例
        :param cls: 类本身
        :param vocab_path: 词汇表文件的路径 (例如 'vocab.txt')
        :return: JiebaTokenizer 实例
        """
        with open(vocab_path, "r", encoding="utf-8") as f:
            # 读取每一行，去掉首尾空白符（如换行符 \n）
            vocab_list = [line.strip() for line in f.readlines()]

        # 使用读取到的列表初始化类实例
        return cls(vocab_list)

    def decode(self, indices):
        """将索引序列解码回词语列表"""
        return [self.index2word.get(idx, self.unk_token) for idx in indices]

    def save(self, path):
        """保存词汇表到文件"""
        with open(path, "w", encoding="utf-8") as f:
            for word in self.vocab_list:
                f.write(word + "\n")

    @classmethod
    def load(cls, path):
        """从文件加载词汇表并创建 tokenizer 实例"""
        with open(path, "r", encoding="utf-8") as f:
            vocab_list = [line.strip() for line in f if line.strip()]
        return cls(vocab_list)
