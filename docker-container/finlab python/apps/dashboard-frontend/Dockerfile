FROM node:18-alpine

WORKDIR /app

# 複製 package.json 和 package-lock.json
COPY package*.json ./

# 安裝依賴
RUN npm install

# 複製源代碼
COPY . .

# 暴露端口
EXPOSE 3000

# 啟動開發服務器
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
