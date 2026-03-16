# Log-Viewer

轻量级日志审计 Web 服务。

## 功能
- 读取 `~/Work/Logs` 目录下最新的 `.log` 文件。
- 提供 `/view` 端点展示最近 100 行日志。
- 支持 Token 鉴权。

## 启动指南

### 1. 设置环境变量
```bash
export LOG_VIEW_TOKEN="your_secure_token_here"
```

### 2. 启动服务
```bash
cd ~/Work/Project/Log-Viewer
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 3. 访问
```bash
http://<YOUR_VPS_IP>:8000/view?token=your_secure_token_here
```
