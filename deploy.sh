#!/bin/bash
set -e

echo "========================================="
echo "  积分管理系统 - 阿里云一键部署脚本"
echo "========================================="

# ---------- 1. 安装 Docker ----------
if ! command -v docker &> /dev/null; then
  echo "[1/4] 安装 Docker..."
  # 阿里云镜像源，国内速度快
  curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo -o /etc/yum.repos.d/docker-ce.repo 2>/dev/null \
    || (curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add - && \
        echo "deb [arch=$(dpkg --print-architecture)] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list && \
        apt-get update)

  # CentOS / RHEL / AlmaLinux
  if command -v yum &> /dev/null; then
    yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  # Ubuntu / Debian
  elif command -v apt-get &> /dev/null; then
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
  else
    echo "不支持的系统，请手动安装 Docker"
    exit 1
  fi

  systemctl enable docker
  systemctl start docker
  echo "Docker 安装完成"
else
  echo "[1/4] Docker 已安装，跳过"
fi

# ---------- 2. 配置 Docker 镜像加速 ----------
DAEMON_JSON="/etc/docker/daemon.json"
if [ ! -f "$DAEMON_JSON" ] || ! grep -q "registry-mirrors" "$DAEMON_JSON"; then
  echo "[2/4] 配置 Docker 镜像加速..."
  mkdir -p /etc/docker
  cat > "$DAEMON_JSON" <<'MIRROR'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://docker.m.daocloud.io"
  ]
}
MIRROR
  systemctl daemon-reload
  systemctl restart docker
  echo "镜像加速配置完成"
else
  echo "[2/4] 镜像加速已配置，跳过"
fi

# ---------- 3. 拉取代码 ----------
APP_DIR="/opt/score-manager"
echo "[3/4] 准备项目代码..."
if [ -d "$APP_DIR" ]; then
  cd "$APP_DIR"
  git pull origin main
else
  git clone https://github.com/weiguang-zz/score-manager-miniprogram.git "$APP_DIR"
  cd "$APP_DIR"
fi

# ---------- 4. 创建 .env（首次部署时生成随机密钥） ----------
ENV_FILE="$APP_DIR/backend/.env"
if [ ! -f "$ENV_FILE" ]; then
  echo "创建 .env 配置文件..."
  JWT_SECRET=$(openssl rand -hex 32)
  cat > "$ENV_FILE" <<ENVFILE
DATABASE_URL=postgresql://scoreapp:scoreapp123@db:5432/scoreapp
JWT_SECRET=${JWT_SECRET}
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ENVFILE
  echo ".env 已生成（JWT_SECRET 已随机生成）"
  echo "⚠️  请修改 $ENV_FILE 中的 ADMIN_PASSWORD 为安全密码"
else
  echo ".env 已存在，跳过"
fi

# ---------- 5. 启动服务 ----------
echo "[4/4] 启动服务..."
cd "$APP_DIR/backend"
docker compose up --build -d

# 等待服务就绪
echo "等待服务启动..."
for i in $(seq 1 30); do
  if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
    break
  fi
  sleep 2
done

# ---------- 6. 验证 ----------
if curl -sf http://localhost:8000/api/health > /dev/null 2>&1; then
  SERVER_IP=$(curl -sf http://ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')
  echo ""
  echo "========================================="
  echo "  部署成功！"
  echo "========================================="
  echo "  API 地址: http://${SERVER_IP}:8000"
  echo "  健康检查: http://${SERVER_IP}:8000/api/health"
  echo "  管理账号: admin / admin123"
  echo ""
  echo "  ⚠️  请记得："
  echo "  1. 在阿里云安全组开放 8000 端口"
  echo "  2. 修改 $ENV_FILE 中的管理员密码"
  echo "  3. 小程序 api.js 中 BASE_URL 改为 http://${SERVER_IP}:8000"
  echo "========================================="
else
  echo "❌ 服务启动失败，请检查日志: docker compose logs"
  exit 1
fi
