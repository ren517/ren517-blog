#!/bin/bash

set -e   # 出错立即停止

cd /home/deploy/blog-source

echo "===== 更新代码 ====="
git fetch origin
git reset --hard origin/main
git clean -fd

echo "===== 构建 Hugo ====="
hugo --minify --gc

echo "===== 发布网站 ====="
rsync -av --delete public/ /var/www/blog/

echo "===== 部署完成 ====="