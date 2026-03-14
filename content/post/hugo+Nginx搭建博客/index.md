+++
author = "ren517"
title = "hugo+Nginx搭建博客"
date = "2026-03-14"
description = "利用轻量博客工具hugo搭建自己的博客"
tags = [
    "hugo",
    "Nginx",
]
categories = [
    "教程",
]
series = ["Themes Guide"]
+++  

本文将介绍在本地搭建 Hugo 并通过Nginx 和 服务器部署 Hugo 的方法。以下所叙之方法就是我在部署本站点时所使用的，防止自己以后忘记。如果对您有借鉴作用，或有问题欢迎留言。

---
在部署 Hugo 之前，需要进行的准备：  
1.购买一个服务器（可以看看阿里云，腾讯云的学生优惠）  
2.租一个域名  
3.下载一个文本编辑器，方便后续写md文件，推荐：vscode  
自动化脚本
```bash
#!/bin/bash

# 切到源码目录
cd /home/deploy/blog-source

# 拉取最新代码
git pull origin main

# 构建 Hugo
hugo --minify

# 同步到 Nginx发布目录
rsync -av --delete public/ /var/www/blog/

# 重新加载 Nginx
sudo systemctl reload nginx
```