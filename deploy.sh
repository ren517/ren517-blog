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
