FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 拷贝代码
COPY . .

# 暴露 Hugging Face 默认端口
EXPOSE 7860

# 启动 FastAPI 服务
CMD ["uvicorn", "server_app.server:app", "--host", "0.0.0.0", "--port", "7860"]