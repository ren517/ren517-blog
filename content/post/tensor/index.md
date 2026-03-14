+++
author = "ren517"
title = "tensor"
date = "2026-03-13"
description = "tensor的一些使用"
tags = [
    "pytorch",
    "tensor",
    "机器学习",
]
categories = [
    "pytorch",
    "机器学习",
]
series = ["Themes Guide"]
+++

## Tensor

```python
import torch
x = torch.randn(2,3,4) # x.shape->[2,3,4]
x.view(2,12) # 三维转换成二维, x.shape->[2,12]
```

x.transpose(1,2) # x.shape->[2,4,3] 交换第一和第二列的维度
x.permute(0,2,1) # x.shape->[2,4,3] 同上


### view 和 reshape的区别


```python
x = torch.rand(3,4)
x = x.transpose(0,1)
print(x.is_contiguous())
# false
x.view(3,4)

# RuntimeError: invalid argument 2: view size is not compatible with input tensor's....
# 内存地址不连续导致该错误

# 把tensor改成内存连续
x = x.contiguous()
x.view(3,4)

# 或可以用reshape解决
x.reshape(3,4)
```

### transopse和permute的区别

transpose()只能一次操作两个维度；permute()可以一次操作多维数据，且必须传入所有维度数，因为permute()的参数是int*。