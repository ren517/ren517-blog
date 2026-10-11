+++
author = "ren517"
title = "记录一下安全仿真课的作业"
date = "2026-10-11"
description = "第一次作业"
tags = [
    "python",
    "学习",
]


categories = [
    "python"
]
series = ["Themes Guide"]
+++

[源代码](https://github.com/ren517/study_test)在链接项目，homework1.py文件

### 1. 平面应力状态计算

力学中，在平面应力状态下，有两个主应力 $(\sigma_1, \sigma_3)$ 作用在某一点上，则最大主应力 $\sigma_1$ 与外法线成 $\alpha$ 角的斜切面上法向应力 $\sigma_\alpha$ 和剪应力 $\tau_\alpha$ 的表达式为：

$$\sigma_\alpha = \frac{\sigma_1 + \sigma_3}{2} + \frac{\sigma_1 - \sigma_3}{2} \cos 2\alpha \tag{1}$$

$$\tau_\alpha = \frac{\sigma_1 - \sigma_3}{2} \sin 2\alpha \tag{2}$$

现已知某点处 $\sigma_1 = 27.3 \times 10^6 \text{Pa}$，$\sigma_3 = 10.7 \times 10^6 \text{Pa}$，分别求 $\alpha = 48°$ 的斜切面上的法向应力 $\sigma_\alpha$ 和剪应力 $\tau_\alpha$。

&gt; **提示：** 该题比较复杂，你需要导入 `math` 模块（`import math`）以利用其中的常量值 `pi` 和三角函数，注意计算时应将角度转换为弧度。请自己设定合适的变量名称。

```python
# 第一题

import math

print("第一题")

sigma_1 = 27.3e6
sigma_3 = 10.7e6
alpha = math.radians(48)  # 角度转弧度

sigma_a = (sigma_1 + sigma_3) / 2 + (sigma_1 - sigma_3) / 2 * math.cos(2 * alpha)
tau_a = (sigma_1 - sigma_3) / 2 * math.sin(2 * alpha)

print(f"法向应力σ_α = {sigma_a:.2f} Pa")
print(f"剪应力τ_α = {tau_a:.2f} Pa")
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第一题
法向应力σ_α = 18132413.75 Pa
剪应力τ_α = 8254531.73 Pa
```

### 2. 保研资格判断

某学院的保送硕士研究生筛选条件是：

1. 通过英语六级考试；
2. 总成绩平均分不低于 80 分；
3. 班级总评排名在前 7 名内，或至少获得过一次国家特等或一等奖学金。

已知某同学通过了英语六级考试，总成绩平均分为 83.2 分，班级总评排名为第 9 名，获得过一次国家一等奖学金，请编程分析该同学是否具备保研资格。（请自行设定合适的变量名称）

```python
# 第二题

print("第二题")

pass_cet6 = True  # 是否通过英语六级
avg_score = 83.2  # 总成绩平均分
rank = 9  # 班级总评排名
has_scholarship = True  # 是否获得过国家特等或一等奖学金

qualified = pass_cet6 and avg_score >= 80 and (rank <= 7 or has_scholarship)

if qualified:
    print("该同学具备保研资格")
else:
    print("该同学不具备保研资格")
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第二题
该同学具备保研资格
```

### 3. 字符串长度

字符串 `'好用的\nVS Cod\x65'` 包含多少个字符？并解释其原因。

```python

# 第三题

print("第三题")

"""
分析：
好用的占三个字符, \n占一个字符,  VS占两个字符, " "占一个字符, Cod占三个字符, \x65占一个字符表示e
总计: 3 + 1 + 2 + 1 + 3 + 1 = 11
"""

s = "好用的\nVS Cod\x65"
print(len(s))  # 11
print(s)  # 好用的 换行 VS Code
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第三题
11
好用的
VS Code
```

### 4. 字符串切片与拼接

从字符串 `'借问酒家何处有？牧童遥指杏花村。'` 中切分出 `'借问'` 和 `'牧童'` 两个分片，并将他们拼接为一个新的字符串。

```python
# 第四题

print("第四题")

my_str = "借问酒家何处有？牧童遥指杏花村。"

str1 = my_str[0:2]  # 切出 '借问'
str2 = my_str[8:10]  # 切出 '牧童'

new_str = str1 + str2
print(new_str)  # 借问牧童
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第四题
借问牧童
```

### 5. 子字符串判断

请在**字符串的方法**中找出一个方法，判断 `'the quick brown fox jumps over a lazy dog'` 中是否包含有 `'jum'` 子字符串。

```python
# 第五题

print("第五题")

"""
str.find(sub[, start[, end]])
Return the lowest index in the string where substring sub is found within the slice s[start:end].
Optional arguments start and end are interpreted as in slice notation. Return -1 if sub is not found.
如果找到了返回索引，如果找不到返回-1
"""

my_str = "'the quick brown fox jumps over a lazy dog'"
is_in_str = my_str.find("jum")
if is_in_str >= 0:
    print(f"{my_str}在改字符串中")
else:
    print(f"{my_str}不在字符串中")
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第五题
'the quick brown fox jumps over a lazy dog'在改字符串中
```

### 6. 字符串格式化

使用字符串格式化，在屏幕上打印自然对数函数的底数 `math.e`，要求小数点后保留 4 个小数位，总体占据 10 个字符的宽度，强制在数字前面加上 +/- 号。

```python

# 第六题
print("第六题")

"""
{value:>+10.4f}
>对齐方式右对齐
+号表示强制打印+/-号
10表示总体占十个字符宽度
.4表示表留4个小数位
f表示易十进制输出

顺序如下：
ormat_spec:             [options][width_and_precision][type]
options:                 [[fill]align][sign]["z"]["#"]["0"]
fill:                    <any character>
align:                   "<" | ">" | "=" | "^"
sign:                    "+" | "-" | " "
width_and_precision:     [width_with_grouping][precision_with_grouping]
width_with_grouping:     [width][grouping]
precision_with_grouping: "." [precision][grouping] | "." grouping
width:                   digit+
precision:               digit+
grouping:                "," | "_"
type:                    "b" | "c" | "d" | "e" | "E" | "f" | "F" | "g"
                         | "G" | "n" | "o" | "s" | "x" | "X" | "%"
"""

temp = math.e
print(f"{temp:>+10.4f}")
```

```bash
PS D:\R\py\study_test> & C:/Users/ren/AppData/Local/Programs/Python/Python314/pyth
第六题
   +2.7183
```
