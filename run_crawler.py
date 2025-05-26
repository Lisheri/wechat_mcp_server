#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序爬虫启动脚本
使用重构后的模块化架构
"""

import sys
import os

# 添加py_scripts目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'py_scripts'))

# 导入主程序
from py_scripts.main import main

if __name__ == "__main__":
    main() 