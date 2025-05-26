# 微信小程序数据抓取MCP服务器 - 使用指南

## 🎯 项目概述

这是一个专门为Mac端微信小程序设计的智能数据抓取系统，具备以下核心功能：

### ✨ 主要特性

1. **自动窗口定位** - 自动查找并聚焦微信窗口
2. **精准区域截取** - 只截取小程序区域，避免干扰
3. **智能页面分析** - AI驱动的页面元素识别
4. **自动化导航** - 自动点击按钮并爬取所有页面
5. **完整数据收集** - 生成结构化的JSON报告

## 🚀 快速开始

### 1. 环境准备

#### 安装Go依赖
```bash
# 安装Go依赖
go mod tidy
```

#### 安装Python依赖
```bash
# 使用自动安装脚本（推荐）
./py_scripts/install_python_dependencies.sh

# 或手动安装
pip3 install requests pillow opencv-python scikit-image pyautogui pyobjc-framework-Cocoa pyobjc-framework-Quartz numpy
```

### 2. 启动MCP服务器

```bash
# 启动Go服务器
go run main.go

# 或使用编译后的二进制文件
./mcp_wechat_mini
```

服务器将在 `http://localhost:8081` 启动

### 3. 准备微信小程序

1. **打开微信** - 确保微信已登录并正常运行
2. **打开小程序** - 在微信中打开要爬取的小程序
3. **调整窗口** - 确保小程序完全可见（爬虫会自动调整窗口大小）

### 4. 运行爬虫

```bash
python3 run_crawler.py
```

## 📋 详细使用流程

### 步骤1：启动服务器
```bash
go run main.go
```

### 步骤2：运行爬虫
```bash
python3 run_crawler.py
```

### 步骤3：按照提示操作
1. 爬虫会自动检查依赖库
2. 自动查找并设置微信窗口
3. 自动点击小程序入口
4. 自动选择第一个小程序
5. 开始自动爬取和分析

## 🔧 配置说明

### 微信窗口配置
在 `py_scripts/config.py` 中可以调整：

```python
# 微信窗口大小和位置
WECHAT_WINDOW_SIZE = (400, 700)
WECHAT_WINDOW_POSITION = (100, 100)

# 小程序区域配置
MINI_PROGRAM_BOUNDS = {
    'x': 150,      # 小程序起始x坐标
    'y': 150,      # 小程序起始y坐标  
    'width': 350,  # 小程序宽度
    'height': 500  # 小程序高度
}
```

### 小程序入口配置
```python
# 小程序入口按钮位置
MINI_PROGRAM_ENTRY_BOUNDS = {
    'x': 30,       # 入口按钮x坐标
    'y': 200,      # 入口按钮y坐标
    'width': 100,  # 按钮宽度
    'height': 100  # 按钮高度
}
```

## 🧪 测试功能

### 运行模块测试
```bash
cd py_scripts && python3 test_modules.py
```

测试内容包括：
- ✅ 配置模块测试
- ✅ 微信窗口管理测试
- ✅ 截图功能测试
- ✅ MCP服务器连接测试

## 📊 输出结果

### 文件结构
```
crawl_results/
├── screenshots/
│   ├── 主页面_normal.png
│   ├── 主页面_full_page.png
│   ├── scroll_0.png
│   ├── scroll_1.png
│   └── ...
├── crawl_results_1234567890.json
└── crawl_report_1234567890.txt
```

### JSON数据格式
```json
{
  "crawl_info": {
    "start_time": "2024-01-01T10:00:00",
    "app_name": "示例小程序",
    "total_pages": 5,
    "total_buttons": 12,
    "crawl_duration": 45.6
  },
  "pages": [
    {
      "page_name": "主页面",
      "timestamp": "2024-01-01T10:00:00",
      "screenshots": {...},
      "analysis": {...},
      "extracted_features": {...}
    }
  ],
  "navigation_map": {
    "查询按钮": "查询页面",
    "设置按钮": "设置页面"
  },
  "feature_summary": {
    "feature_count": 3,
    "feature_categories": {
      "查询": 2,
      "设置": 1
    }
  }
}
```

## ⚠️ 注意事项

### 系统权限
- 需要授予Python访问屏幕录制权限
- 可能需要授予自动化操作权限

### 使用建议
- 爬取期间避免操作其他窗口
- 确保网络连接稳定
- 关闭系统通知避免干扰

### 兼容性
- 专门为Mac系统优化
- 支持最新版本的Mac微信客户端
- 兼容各种屏幕分辨率

## 🛠️ 故障排除

### 常见问题

#### 1. 找不到微信窗口
**解决方案：**
- 确保微信已打开并可见
- 检查微信是否在前台运行
- 重启微信应用

#### 2. 小程序入口检测失败
**解决方案：**
- 检查微信界面是否正常
- 确保小程序入口可见
- 调整配置中的入口位置参数

#### 3. 截图区域错误
**解决方案：**
- 检查小程序是否完全显示
- 调整配置中的区域参数
- 确保微信窗口大小正确

#### 4. 模块导入失败
**解决方案：**
- 检查Python路径设置
- 确保在正确的目录运行
- 重新安装依赖库

### 获取帮助
- 运行模块测试: `cd py_scripts && python3 test_modules.py`
- 查看详细日志输出
- 参考README文档

## 🔄 高级功能

### 自定义配置
可以根据不同的小程序调整配置参数：

```python
# 针对不同小程序的配置
MINI_PROGRAM_CONFIGS = {
    "游戏类": {
        "bounds": {"x": 100, "y": 100, "width": 400, "height": 600},
        "entry": {"x": 50, "y": 250}
    },
    "工具类": {
        "bounds": {"x": 150, "y": 150, "width": 350, "height": 500},
        "entry": {"x": 30, "y": 200}
    }
}
```

### 批量处理
可以扩展脚本支持多个小程序的批量爬取。

## 📈 性能优化

### 提高爬取速度
- 调整 `CLICK_DELAY` 和 `PAGE_LOAD_DELAY`
- 减少 `MAX_SCROLLS` 数量
- 优化截图分辨率

### 提高准确性
- 增加 `ANALYSIS_TIMEOUT` 时间
- 调整 `SIMILARITY_THRESHOLD` 阈值
- 使用更精确的坐标配置

---

**🎯 专为Mac端微信小程序设计的智能爬虫系统** 