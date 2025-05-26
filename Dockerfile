# 使用多阶段构建
# 第一阶段：构建阶段
FROM hub-mirror.c.163.com/library/golang:1.20-alpine AS builder

# 安装依赖
RUN apk add --no-cache git ca-certificates tzdata

# 设置工作目录
WORKDIR /app

# 复制go.mod和go.sum
COPY go.mod ./

# 下载依赖
RUN go mod download

# 复制源代码
COPY . .

# 构建应用程序
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o mcp_wechat_mini .

# 第二阶段：运行阶段
FROM chromedp/headless-shell:latest

# 安装运行时依赖
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 从builder阶段复制编译好的应用程序
COPY --from=builder /app/mcp_wechat_mini /app/
COPY --from=builder /app/config.yaml /app/

# 设置时区
ENV TZ=Asia/Shanghai

# 暴露端口
EXPOSE 8080

# 设置入口点
ENTRYPOINT ["/app/mcp_wechat_mini"] 