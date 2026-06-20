FROM node:20-alpine as builder

WORKDIR /app

# 复制依赖文件
COPY package.json package-lock.json* ./

# 安装依赖
RUN npm install

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 3000

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]
