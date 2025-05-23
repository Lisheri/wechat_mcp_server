# 微信小程序数据抓取服务 (MCP Server)

这是一个用于抓取微信小程序页面数据的服务器，使用Golang编写。

## 功能特点

- 抓取微信小程序页面内容
- 获取页面截图
- 提取页面元数据（组件、API调用、资源等）
- RESTful API接口
- 支持并发抓取
- 支持自定义抓取参数
- 完整的日志记录

## 技术栈

- Golang
- Gin Web框架
- Chromedp (基于Chrome的无头浏览器)
- YAML配置
- Logrus日志系统

## 环境要求

- Go 1.18+
- Chrome浏览器（抓取时需要）

## 安装指南

### 从源码构建

1. 克隆代码仓库
   ```bash
   git clone https://github.com/yourusername/mcp_wechat_mini.git
   cd mcp_wechat_mini
   ```

2. 安装依赖
   ```bash
   go mod download
   ```

3. 编译
   ```bash
   go build -o mcp_wechat_mini
   ```

### 使用Docker

1. 构建Docker镜像
   ```bash
   docker build -t mcp_wechat_mini .
   ```

2. 运行容器
   ```bash
   docker run -p 8080:8080 mcp_wechat_mini
   ```

## 配置

配置文件位于`config.yaml`，包含以下主要部分：

- `server`: 服务器配置（监听地址、超时设置）
- `wechat`: 微信小程序配置（AppID、AppSecret）
- `scraper`: 抓取器配置（用户代理、超时、并发等）
- `database`: 数据库配置

## 使用方法

### 启动服务

```bash
./mcp_wechat_mini
```

或者指定配置文件路径：

```bash
./mcp_wechat_mini -config=/path/to/config.yaml
```

### API接口

#### 抓取小程序页面

```
POST /api/v1/wechat-mini/scrap
```

请求体示例：

```json
{
  "appId": "wx1234567890abcdef",
  "pagePath": "pages/index/index",
  "params": {
    "query1": "value1",
    "query2": "value2"
  },
  "options": {
    "screenshotEnabled": true,
    "metadataEnabled": true,
    "maxWaitTime": 30
  }
}
```

响应示例：

```json
{
  "success": true,
  "message": "抓取成功",
  "data": {
    "id": 0,
    "appId": "wx1234567890abcdef",
    "pagePath": "pages/index/index",
    "title": "小程序页面标题",
    "content": "<!DOCTYPE html><html>...</html>",
    "screenshot": "base64编码的图片...",
    "createdAt": "2023-08-10T12:34:56Z",
    "updatedAt": "2023-08-10T12:34:56Z",
    "metadata": {
      "components": [
        {
          "name": "wx-view",
          "count": 15,
          "props": {},
          "location": ""
        }
      ],
      "apis": [],
      "resources": [
        {
          "type": "image",
          "url": "https://example.com/image.jpg",
          "size": 0,
          "mimeType": ""
        }
      ]
    }
  },
  "duration": 1234
}
```

#### 获取历史记录

```
GET /api/v1/wechat-mini/history
```

#### 获取指定页面详情

```
GET /api/v1/wechat-mini/page/:id
```

## 开发扩展

### 添加新功能

1. 在相应的包中实现功能
2. 在控制器中添加API接口
3. 更新配置文件（如需要）

### 代码结构

- `config/`: 配置管理
- `controller/`: HTTP请求处理
- `logger/`: 日志系统
- `model/`: 数据模型
- `server/`: HTTP服务器
- `service/`: 业务逻辑

## 许可证

[MIT License](LICENSE) 