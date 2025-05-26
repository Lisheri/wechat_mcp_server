#!/bin/bash

echo "🐍 微信小程序爬虫 - Python依赖安装脚本"
echo "================================================"

# 检查Python版本
echo "🔍 检查Python版本..."
python3 --version

if [ $? -ne 0 ]; then
    echo "❌ Python3未安装，请先安装Python3"
    exit 1
fi

echo "✅ Python3已安装"

# 升级pip
echo ""
echo "📦 升级pip..."
python3 -m pip install --upgrade pip

# 安装基础依赖
echo ""
echo "📚 安装基础依赖库..."
python3 -m pip install requests

# 安装图像处理依赖
echo ""
echo "🖼️ 安装图像处理依赖..."
python3 -m pip install pillow opencv-python scikit-image

# 安装自动化依赖
echo ""
echo "🤖 安装自动化依赖..."
python3 -m pip install pyautogui

# 安装Mac系统集成依赖
echo ""
echo "🍎 安装Mac系统集成依赖..."
python3 -m pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz

# 安装数据处理依赖
echo ""
echo "📊 安装数据处理依赖..."
python3 -m pip install numpy

echo ""
echo "✅ 所有依赖安装完成！"
echo ""
echo "📋 已安装的库："
echo "   - requests: HTTP请求库"
echo "   - pillow: 图像处理库"
echo "   - opencv-python: 计算机视觉库"
echo "   - scikit-image: 图像分析库"
echo "   - pyautogui: 自动化操作库"
echo "   - pyobjc-framework-Cocoa: Mac系统集成"
echo "   - pyobjc-framework-Quartz: Mac图形系统"
echo "   - numpy: 数值计算库"
echo ""
echo "🚀 现在可以运行爬虫了："
echo "   python3 wechat_mini_crawler.py" 