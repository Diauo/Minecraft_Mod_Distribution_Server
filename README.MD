# Minecraft Mod Update Server

## 简介
本项目用于自动化管理Minecraft Mod更新，支持Windows与Android客户端。

## 快速启动
1. 安装依赖：`pip install -r requirements.txt`
2. 启动服务：`python server.py`
3. 访问Web界面：`http://localhost:5000/diauo`

## 部署
- 本地运行：`./scripts/start_server.sh`
- Docker部署：`docker build -t mc_update_server . && docker run -p 8000:8000 mc_update_server`