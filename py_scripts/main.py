#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序自动化爬虫主程序
使用模块化架构，支持自动小程序入口检测和精准截图
"""

import sys
import pyautogui
from crawler_core import CrawlerCore
from config import CrawlerConfig

def check_dependencies():
    """检查依赖库是否正确安装"""
    print("🔍 正在检查依赖库...")
    missing_deps = []
    
    try:
        import pyautogui
        print("✅ pyautogui - 自动化操作库")
    except ImportError:
        missing_deps.append("pyautogui")
        print("❌ pyautogui - 自动化操作库")
    
    try:
        import cv2
        print("✅ opencv-python - 图像处理库")
    except ImportError:
        missing_deps.append("opencv-python")
        print("❌ opencv-python - 图像处理库")
    
    try:
        from PIL import Image
        print("✅ pillow - 图像处理库")
    except ImportError:
        missing_deps.append("pillow")
        print("❌ pillow - 图像处理库")
    
    try:
        from skimage.metrics import structural_similarity
        print("✅ scikit-image - 图像分析库")
    except ImportError:
        missing_deps.append("scikit-image")
        print("❌ scikit-image - 图像分析库")
    
    try:
        from AppKit import NSWorkspace
        print("✅ pyobjc-framework-Cocoa - Mac系统集成")
    except ImportError:
        missing_deps.append("pyobjc-framework-Cocoa")
        print("❌ pyobjc-framework-Cocoa - Mac系统集成")
    
    if missing_deps:
        print(f"\n❌ 缺少 {len(missing_deps)} 个依赖库")
        print("请运行以下命令安装:")
        print(f"pip install {' '.join(missing_deps)}")
        return False
    
    print("\n✅ 所有依赖库检查通过")
    return True

def setup_pyautogui():
    """设置PyAutoGUI配置"""
    pyautogui.FAILSAFE = CrawlerConfig.PYAUTOGUI_FAILSAFE
    pyautogui.PAUSE = CrawlerConfig.PYAUTOGUI_PAUSE
    print(f"⚙️ PyAutoGUI配置完成 (PAUSE={CrawlerConfig.PYAUTOGUI_PAUSE}s)")

def main():
    """主函数"""
    print("🤖 微信小程序自动化爬虫 v2.0")
    print("=" * 50)
    print("🎯 专门针对Mac端微信小程序的智能爬虫")
    print("✨ 新功能：自动小程序入口检测，精准截图区域")
    print("")
    
    # 检查依赖
    if not check_dependencies():
        print("\n💡 请先安装缺失的依赖库:")
        print("   ./install_python_dependencies.sh")
        sys.exit(1)
    
    # 设置PyAutoGUI
    setup_pyautogui()
    
    # 使用说明
    print("\n📋 使用说明:")
    print("1. 确保微信已打开并登录")
    print("2. 爬虫将自动定位微信窗口")
    print("3. 自动点击小程序入口并选择第一个小程序")
    print("4. 自动截取小程序区域进行分析")
    print("5. 自动点击按钮并爬取所有页面")
    print("")
    
    # 获取小程序名称
    app_name = input("请输入小程序名称 (默认: 微信小程序): ").strip()
    if not app_name:
        app_name = "微信小程序"
    
    print(f"\n🚀 准备爬取小程序: {app_name}")
    print("💡 提示：爬取过程中请不要移动鼠标或操作其他窗口")
    
    # 创建爬虫实例并开始爬取
    try:
        crawler = CrawlerCore()
        success = crawler.start_crawling(app_name)
        
        if success:
            print("\n🎉 爬取成功完成！")
        else:
            print("\n❌ 爬取失败")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断爬取")
    except Exception as e:
        print(f"\n❌ 爬取过程中出现错误: {e}")
        print("💡 可能的解决方案:")
        print("   - 确保微信已打开且可见")
        print("   - 检查MCP服务器是否正在运行")
        print("   - 确保网络连接正常")
        print("   - 检查系统权限设置")
    
    print("\n👋 爬取结束")
    print("📁 结果文件保存在 crawl_results/ 目录中")

if __name__ == "__main__":
    main() 