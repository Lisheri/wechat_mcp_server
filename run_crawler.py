#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序爬虫 - 主启动脚本
"""

import sys
import os

# 添加py_scripts目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py_scripts'))

if __name__ == "__main__":
    print("🚀 微信小程序爬虫 v2.1")
    print("=" * 40)
    print("✨ 新功能:")
    print("   - 智能动态检测小程序界面")
    print("   - 无需固定坐标配置")
    print("   - 自动识别小程序入口和图标")
    print("   - 基于计算机视觉的界面分析")
    print()
    print("📋 使用说明:")
    print("1. 确保微信已打开")
    print("2. 可以在任何界面启动（主界面、小程序列表、小程序内）")
    print("3. 爬虫会自动检测当前状态并进入小程序")
    print()
    
    try:
        from main import main
        main()
    except KeyboardInterrupt:
        print("\n👋 用户中断，程序退出")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        sys.exit(1) 