#!/bin/bash

set -e

echo "==== Phase 1-3 Full Deployment Script ===="

APP_DIR=/opt/openclaw

MYSQL_ROOT_PASSWORD=Root123456!
MYSQL_DATABASE=fastapi_pdf
MYSQL_USER=app
MYSQL_PASSWORD=app123456
SECRET_KEY=$(openssl rand -hex 32)

echo "Installing Docker..."
apt update
apt install -y ca-certificates curl gnupg lsb-release

mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" \
  > /etc/apt/sources.list.d/docker.list

apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable docker
systemctl start docker

echo "Creating application directory..."
mkdir -p $APP_DIR
cd $APP_DIR

echo "Creating .env file..."
cat > .env <<EOF
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
MYSQL_DATABASE=$MYSQL_DATABASE
MYSQL_USER=$MYSQL_USER
MYSQL_PASSWORD=$MYSQL_PASSWORD
SECRET_KEY=$SECRET_KEY
DATABASE_URL=mysql+pymysql://$MYSQL_USER:$MYSQL_PASSWORD@mysql:3306/$MYSQL_DATABASE
REDIS_URL=redis://redis:6379/0
EOF

echo "Starting containers..."
docker compose up -d

echo "Deployment complete."
