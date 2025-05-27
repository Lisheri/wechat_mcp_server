#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序自动化爬虫主程序
直接对当前已打开的小程序进行截图和按钮点击操作
"""

import sys
import pyautogui
from crawler_core import CrawlerCore
from config import CrawlerConfig
from app_config import get_app_name_from_config, get_preset_apps, is_verbose_logging

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
    
    try:
        import pygetwindow as gw
        print("✅ pygetwindow - 系统窗口检测")
    except ImportError:
        missing_deps.append("pygetwindow")
        print("❌ pygetwindow - 系统窗口检测")
    
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

def show_preset_options():
    """显示预设选项"""
    preset_apps = get_preset_apps()
    print("🔢 快速选择 (输入数字):")
    for i, app in enumerate(preset_apps, 1):
        print(f"   {i}. {app}")
    print(f"   0. 手动输入")
    print("")

def get_app_name():
    """获取小程序名称的改进输入函数"""
    # 首先检查配置文件是否设置了跳过输入
    config_name = get_app_name_from_config()
    if config_name:
        print(f"📝 从配置文件读取小程序名称: {config_name}")
        return config_name
    
    default_name = "微信小程序"
    preset_apps = get_preset_apps()
    
    print("📝 小程序名称选择:")
    print("💡 如果遇到输入问题，您可以:")
    print("   1. 使用数字快速选择")
    print("   2. 按回车使用默认名称")
    print("   3. 输入 'skip' 跳过输入环节")
    print("   4. 修改 app_config.py 中的 'skip_input': True 自动跳过")
    print("")
    
    show_preset_options()
    
    max_attempts = 3
    attempt = 1
    
    while attempt <= max_attempts:
        try:
            print(f"💡 提示: 如果输入框无法删除内容，试试 Ctrl+A 全选后重新输入")
            user_input = input(f"请选择或输入小程序名称 (默认: {default_name}): ")
            
            # 处理输入
            user_input = user_input.strip()
            
            # 检查是否是数字选择
            if user_input.isdigit():
                choice = int(user_input)
                if choice == 0:
                    # 手动输入
                    manual_input = input("请输入小程序名称: ").strip()
                    if manual_input:
                        print(f"✅ 使用手动输入的名称: {manual_input}")
                        return manual_input
                    else:
                        print(f"✅ 使用默认名称: {default_name}")
                        return default_name
                elif 1 <= choice <= len(preset_apps):
                    selected_app = preset_apps[choice - 1]
                    print(f"✅ 选择预设应用: {selected_app}")
                    return selected_app
                else:
                    print(f"⚠️ 无效选择，请输入 0-{len(preset_apps)} 之间的数字")
                    continue
            elif user_input.lower() == 'skip':
                print("⏭️ 跳过输入，使用默认名称")
                return default_name
            elif not user_input:
                print(f"✅ 使用默认名称: {default_name}")
                return default_name
            else:
                print(f"✅ 使用输入的名称: {user_input}")
                return user_input
                
        except (EOFError, KeyboardInterrupt):
            print(f"\n⚠️ 输入中断，使用默认名称: {default_name}")
            return default_name
        except ValueError:
            print(f"⚠️ 输入格式错误，请输入数字或文本")
            continue
        except Exception as e:
            print(f"⚠️ 输入出现问题 (尝试 {attempt}/{max_attempts}): {e}")
            if attempt == max_attempts:
                print(f"🔄 多次输入失败，使用默认名称: {default_name}")
                return default_name
            else:
                print("🔄 正在重试...")
                attempt += 1
    
    return default_name

def main():
    """主函数"""
    print("🤖 微信小程序自动化爬虫 v2.1 (模块化版本)")
    print("=" * 55)
    print("🎯 直接对当前已打开的小程序进行截图和按钮点击")
    print("✨ 新功能：系统级窗口检测，精确截图边界")
    print("🚀 架构：模块化设计，高度可维护")
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
    print("1. 请确保微信小程序已经打开并显示在屏幕上")
    print("2. 爬虫将自动检测小程序窗口位置")
    print("3. 自动截取小程序区域进行分析")
    print("4. 自动点击按钮并爬取所有页面")
    print("5. 爬取过程中请不要移动鼠标或操作其他窗口")
    print("")
    
    # 获取小程序名称 - 使用改进的输入函数
    app_name = get_app_name()
    
    print(f"\n🚀 准备爬取小程序: {app_name}")
    print("💡 提示：请确保小程序已经打开并可见")
    
    # 等待用户确认
    try:
        input("\n按回车键开始检测小程序窗口并开始爬取...")
    except (EOFError, KeyboardInterrupt):
        print("\n⏹️ 用户取消操作")
        sys.exit(0)
    
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
        print("   - 确保小程序已打开且可见")
        print("   - 检查MCP服务器是否正在运行")
        print("   - 确保网络连接正常")
        print("   - 检查系统权限设置")
    
    print("\n👋 爬取结束")
    print("📁 结果文件保存在 crawl_results/ 目录中")

if __name__ == "__main__":
    main() 