#!/bin/bash
# 阿里云服务器初始化脚本（首次运行一次即可）
# 用法：ssh root@<your-ip> 'bash -s' < scripts/server-init.sh

set -e

echo "=== 安装 Docker ==="
if ! command -v docker &>/dev/null; then
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

echo "=== 安装 Docker Compose 插件 ==="
if ! docker compose version &>/dev/null; then
    apt-get update && apt-get install -y docker-compose-plugin
fi

echo "=== 创建部署目录 ==="
mkdir -p /opt/heyiyun/website /opt/heyiyun/infra/nginx /opt/heyiyun/scripts

echo "=== 生成 SSH 部署密钥（若不存在）==="
if [ ! -f ~/.ssh/id_ed25519 ]; then
    ssh-keygen -t ed25519 -C "heyiyun-deploy" -f ~/.ssh/id_ed25519 -N ""
    echo ""
    echo ">>> 将以下公钥添加到 GitHub 账号的 Deploy Keys >>>"
    cat ~/.ssh/id_ed25519.pub
    echo ""
fi

echo "=== 开放防火墙端口 ==="
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

echo ""
echo "✅ 初始化完成！"
echo ""
echo "下一步：在 GitHub 仓库 Settings → Secrets and variables → Actions 中添加："
echo "  ALIYUN_HOST        = 服务器公网 IP"
echo "  ALIYUN_USER        = root（或你的用户名）"
echo "  ALIYUN_SSH_KEY     = 服务器 ~/.ssh/id_ed25519 私钥内容"
echo "  SECRET_KEY         = 随机长字符串（JWT 密钥）"
echo "  POSTGRES_PASSWORD  = 数据库密码"
echo "  MINIO_PASSWORD     = MinIO 密码"
echo "  DOMAIN             = 你的域名（可选，没有填 IP 也行）"
