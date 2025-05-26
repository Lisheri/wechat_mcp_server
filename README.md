# 微信小程序数据抓取MCP服务器 v2.1

## 🎯 项目简介

这是一个专门为**Mac端微信小程序**设计的智能数据抓取系统，采用MCP（Model Context Protocol）架构，结合Go后端服务和Python自动化爬虫，实现对微信小程序的全自动数据收集和分析。

## ✨ v2.1 重大更新

### 🔥 新功能亮点

1. **🎯 自动小程序入口检测** - 自动点击小程序入口并选择第一个小程序
2. **📱 精准小程序截图** - 只截取小程序区域，避免全屏干扰
3. **🧹 智能截图清理** - 每次爬取前自动清理旧截图文件
4. **🏗️ 模块化架构** - 代码拆分为多个专门模块，每个文件专注单一功能
5. **⚡ 更好的错误处理** - 智能重试和用户友好的错误提示

### 🏗️ 架构重构

#### 模块化设计
```
py_scripts/
├── config.py                    # 配置管理 (70行)
├── wechat_window_manager.py     # 微信窗口管理 (95行)
├── screenshot_manager.py        # 截图管理 (85行)
├── interaction_manager.py       # 交互管理 (90行)
├── analysis_client.py           # 分析客户端 (85行)
├── data_manager.py              # 数据管理 (95行)
├── crawler_core.py              # 爬虫核心 (90行)
├── main.py                      # 主程序 (75行)
└── test_modules.py              # 模块测试 (70行)
```

#### 单一职责原则
- **配置管理**: 所有配置常量和设置
- **窗口管理**: 微信窗口查找、聚焦、小程序入口处理
- **截图管理**: 截图、滚动截图、图片处理
- **交互管理**: 点击、返回等交互操作
- **分析客户端**: 与MCP服务器通信和图像分析
- **数据管理**: 数据收集、存储和报告生成
- **爬虫核心**: 整合所有组件的主要爬取逻辑

### 🆚 版本对比

| 功能 | v2.0 | v2.1 |
|------|------|------|
| 代码结构 | 单文件900+行 | 🏗️ 模块化8个文件，每个<100行 |
| 小程序入口 | 手动操作 | 🎯 自动检测和点击 |
| 截图清理 | 手动清理 | 🧹 自动清理旧文件 |
| 代码维护 | 难以维护 | ✨ 易于维护和扩展 |
| 功能测试 | 整体测试 | 🧪 模块化测试 |

## 🚀 快速开始

### 1. 环境要求

- **操作系统**: macOS（专门优化）
- **Go版本**: 1.19+
- **Python版本**: 3.7+
- **微信**: Mac版微信客户端

### 2. 一键安装

```bash
# 克隆项目
git clone <repository-url>
cd mcp_wechat_mini

# 安装Go依赖
go mod tidy

# 安装Python依赖（一键脚本）
./py_scripts/install_python_dependencies.sh
```

### 3. 启动服务

```bash
# 启动MCP服务器
go run main.go
```

### 4. 运行爬虫

```bash
# 使用新的模块化爬虫
python3 run_crawler.py

# 或直接运行
cd py_scripts && python3 main.py
```

## 🔧 核心功能

### 🤖 智能自动化

- **自动窗口检测**: 使用AppleScript自动查找微信窗口
- **自动小程序入口**: 自动点击小程序入口并选择第一个小程序
- **智能区域识别**: 精确定位小程序显示区域
- **自适应截图**: 根据小程序大小动态调整截图区域
- **智能滚动**: 自动检测页面底部，避免无效滚动

### 🧠 AI驱动分析

- **文本提取**: OCR识别页面所有文本内容
- **按钮检测**: 智能识别各种类型的交互元素
- **图标分析**: 自动分类图标功能和用途
- **布局解析**: 分析页面结构和设计模式
- **功能分类**: 基于内容智能分类页面功能

### 📊 数据收集

- **完整页面数据**: 包含截图、分析结果、功能特征
- **导航关系映射**: 记录页面间的跳转关系
- **功能总结报告**: 生成小程序功能概览
- **结构化输出**: JSON格式的完整数据

## 📁 项目结构

```
mcp_wechat_mini/
├── main.go                          # Go服务器入口
├── config/                          # 配置管理
├── logger/                          # 日志系统
├── model/                           # 数据模型
├── service/                         # 业务逻辑
├── controller/                      # API控制器
├── py_scripts/                      # Python爬虫模块
│   ├── config.py                    # 爬虫配置
│   ├── wechat_window_manager.py     # 微信窗口管理
│   ├── screenshot_manager.py        # 截图管理
│   ├── interaction_manager.py       # 交互管理
│   ├── analysis_client.py           # 分析客户端
│   ├── data_manager.py              # 数据管理
│   ├── crawler_core.py              # 爬虫核心
│   ├── main.py                      # 主程序
│   ├── test_modules.py              # 模块测试
│   └── install_python_dependencies.sh # 依赖安装
├── run_crawler.py                   # 爬虫启动脚本
├── config.yaml                      # 服务器配置
├── USAGE_GUIDE.md                   # 详细使用指南
└── README.md                        # 项目说明
```

## 🎮 使用流程

### 步骤1: 准备环境
1. 确保微信已打开并登录
2. 启动MCP服务器

### 步骤2: 运行爬虫
```bash
python3 run_crawler.py
```

### 步骤3: 自动化执行
- 🔍 自动检测微信窗口
- 📱 自动点击小程序入口
- 🎯 自动选择第一个小程序
- 📸 智能截图和分析
- 🖱️ 自动点击和导航
- 📊 生成完整报告

## 📊 输出示例

### 文件输出
```
crawl_results/
├── screenshots/
│   ├── 主页面_normal.png
│   ├── 主页面_full_page.png
│   └── 功能页面_normal.png
├── crawl_results_1234567890.json
└── crawl_report_1234567890.txt
```

### JSON数据结构
```json
{
  "crawl_info": {
    "app_name": "示例小程序",
    "total_pages": 5,
    "total_buttons": 12,
    "crawl_duration": 45.6
  },
  "pages": [...],
  "navigation_map": {...},
  "feature_summary": {...}
}
```

## 🧪 测试功能

### 模块测试
```bash
cd py_scripts && python3 test_modules.py
```

### 测试内容
- ✅ 配置模块测试
- ✅ 微信窗口管理测试
- ✅ 截图功能测试
- ✅ MCP服务器连接测试

## 🛠️ 技术架构

### 后端服务 (Go)
- **Gin框架**: 高性能HTTP服务器
- **Chromedp**: 无头浏览器控制
- **Logrus**: 结构化日志系统
- **YAML配置**: 灵活的配置管理

### 前端爬虫 (Python)
- **PyAutoGUI**: 自动化操作库
- **OpenCV**: 图像处理和分析
- **PIL/Pillow**: 图像操作和处理
- **scikit-image**: 高级图像分析
- **PyObjC**: Mac系统集成

### 数据流程
```
微信小程序 → 自动入口检测 → 精准截图 → AI分析 → 结构化数据 → JSON输出
```

## 🔧 配置选项

### 服务器配置 (config.yaml)
```yaml
server:
  address: ":8081"
  readTimeout: 30s
  writeTimeout: 30s

screenshot:
  max_file_size: 10485760
  analysis_timeout: 60
  supported_formats: ["png", "jpg", "jpeg"]
```

### 爬虫配置 (py_scripts/config.py)
```python
# 微信窗口配置
WECHAT_WINDOW_SIZE = (400, 700)
WECHAT_WINDOW_POSITION = (100, 100)

# 小程序区域配置
MINI_PROGRAM_BOUNDS = {
    'x': 150, 'y': 150,
    'width': 350, 'height': 500
}

# 小程序入口按钮位置
MINI_PROGRAM_ENTRY_BOUNDS = {
    'x': 30, 'y': 200,
    'width': 100, 'height': 100
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
1. **找不到微信窗口** → 确保微信已打开
2. **小程序入口检测失败** → 检查微信界面是否正常
3. **截图区域错误** → 检查小程序是否完全显示
4. **模块导入失败** → 检查Python路径设置

### 获取帮助
- 运行模块测试: `cd py_scripts && python3 test_modules.py`
- 查看详细日志输出
- 参考使用指南文档

## 🔄 版本历史

### v2.1 (当前版本)
- ✅ 模块化架构重构
- ✅ 自动小程序入口检测
- ✅ 智能截图清理
- ✅ 单一职责原则设计
- ✅ 完善的模块测试

### v2.0
- ✅ 自动微信窗口定位
- ✅ 精准小程序区域截图
- ✅ 智能坐标转换系统
- ✅ 增强的返回功能

### v1.0
- ✅ 基础截图和分析功能
- ✅ 手动操作模式
- ✅ JSON数据输出

## 🚀 未来计划

- 🔄 支持多个小程序同时爬取
- 🔄 添加更多手势操作支持
- 🔄 实现自定义爬取规则
- 🔄 添加实时预览功能
- 🔄 支持Windows和Linux系统

## 📄 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目！

---

**🎯 专为Mac端微信小程序设计的智能爬虫系统 - 模块化架构，更易维护和扩展** 