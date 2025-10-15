FROM python:3.11-slim

WORKDIR /app

# 複製 requirements.txt
COPY trending-api/requirements.txt .

# 安裝依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製 dashboard-api 的源碼以使用 CMoneyClient
COPY dashboard-api/src ./src

# 複製 trending-api 的源碼（除了 src 目錄）
COPY trending-api/main.py .
COPY trending-api/requirements.txt .

# 複製 trending-api 的 agents 到 src/agents
COPY trending-api/src/agents ./src/agents

EXPOSE 8004

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8004"]

