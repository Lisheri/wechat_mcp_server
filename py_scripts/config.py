#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫配置文件
包含所有配置常量和设置
"""

import os
from datetime import datetime

class CrawlerConfig:
    """爬虫配置类"""
    
    # 服务器配置
    SERVER_URL = "http://localhost:8081"
    
    # 目录配置
    OUTPUT_DIR = "crawl_results"
    SCREENSHOTS_DIR = os.path.join(OUTPUT_DIR, "screenshots")
    
    # 微信窗口配置 - 增加宽度以完整覆盖小程序内容
    WECHAT_WINDOW_SIZE = (500, 800)  # 从400x700增加到500x800
    WECHAT_WINDOW_POSITION = (100, 100)
    
    # 小程序区域配置（相对于微信窗口）
    MINI_PROGRAM_BOUNDS = {
        'x': 9,        # 小程序起始x坐标（基于精确检测结果）
        'y': 49,       # 小程序起始y坐标（基于精确检测结果）
        'width': 405,  # 小程序宽度（基于精确检测结果，接近414像素）
        'height': 701  # 小程序高度（基于精确检测结果）
    }
    
    # 小程序入口按钮位置（在小程序列表页面）
    MINI_PROGRAM_ENTRY_BOUNDS = {
        'x': 30,       # 小程序入口按钮x坐标
        'y': 200,      # 小程序入口按钮y坐标
        'width': 100,  # 按钮宽度
        'height': 100  # 按钮高度
    }
    
    # 操作配置
    CLICK_DELAY = 2.0          # 点击后等待时间
    SCROLL_DELAY = 1.0         # 滚动后等待时间
    PAGE_LOAD_DELAY = 3.0      # 页面加载等待时间
    FOCUS_DELAY = 0.5          # 聚焦等待时间
    
    # 滚动配置
    MAX_SCROLLS = 10           # 最大滚动次数
    SCROLL_DISTANCE = 3        # 滚动距离
    SIMILARITY_THRESHOLD = 0.95 # 截图相似度阈值
    
    # 返回按钮位置（相对于小程序区域）
    BACK_BUTTON_POSITIONS = [
        (20, 30),   # 典型的返回按钮位置
        (30, 40),   # 备选位置1
        (15, 25),   # 备选位置2
    ]
    
    # PyAutoGUI配置
    PYAUTOGUI_PAUSE = 1.0      # PyAutoGUI操作间隔
    PYAUTOGUI_FAILSAFE = True  # 启用安全模式
    
    # 分析配置
    ANALYSIS_TIMEOUT = 60      # 分析超时时间
    
    @classmethod
    def create_output_dirs(cls):
        """创建输出目录"""
        os.makedirs(cls.OUTPUT_DIR, exist_ok=True)
        os.makedirs(cls.SCREENSHOTS_DIR, exist_ok=True)
    
    @classmethod
    def clean_screenshots(cls):
        """清理旧的截图文件"""
        if os.path.exists(cls.SCREENSHOTS_DIR):
            for filename in os.listdir(cls.SCREENSHOTS_DIR):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(cls.SCREENSHOTS_DIR, filename)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 已删除旧截图: {filename}")
                    except Exception as e:
                        print(f"⚠️ 删除截图失败: {filename} - {e}")
    
    @classmethod
    def get_timestamp_filename(cls, prefix="", suffix=".png"):
        """生成带时间戳的文件名"""
        timestamp = int(datetime.now().timestamp())
        return f"{prefix}_{timestamp}{suffix}" if prefix else f"{timestamp}{suffix}" 