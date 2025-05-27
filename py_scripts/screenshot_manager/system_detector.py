#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统窗口检测器
基于操作系统窗口信息检测小程序区域（类似Snipaste的实现）
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageGrab
import pygetwindow as gw
from config import CrawlerConfig
from .utils import ScreenshotUtils
from .window_analyzer import WindowContentAnalyzer


class SystemWindowDetector:
    """系统窗口检测器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
        self.analyzer = WindowContentAnalyzer()
    
    def detect_miniprogram_window(self):
        """通过系统窗口信息检测小程序区域"""
        try:
            print("🔍 开始系统级窗口检测...")
            
            # 获取所有窗口标题
            all_titles = gw.getAllTitles()
            print(f"📊 检测到 {len(all_titles)} 个窗口标题")
            
            # 查找微信相关窗口
            wechat_titles = self._find_wechat_windows(all_titles)
            
            if not wechat_titles:
                print("⚠️ 未找到微信相关窗口")
                return None
            
            # 分析每个微信窗口，寻找小程序内容
            for title in wechat_titles:
                result = self._analyze_window(title)
                if result:
                    return result
            
            print("⚠️ 在所有微信窗口中都未找到小程序区域")
            return None
            
        except Exception as e:
            print(f"⚠️ 系统窗口检测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _find_wechat_windows(self, all_titles):
        """查找微信相关窗口"""
        wechat_titles = []
        wechat_keywords = ['微信', 'WeChat', '向僧户小助手', '小助手']
        
        for title in all_titles:
            if title and any(keyword in title for keyword in wechat_keywords):
                wechat_titles.append(title)
                print(f"🔍 发现微信相关窗口: '{title}'")
        
        return wechat_titles
    
    def _analyze_window(self, title):
        """分析单个窗口"""
        try:
            # 获取窗口几何信息
            window_geometry = gw.getWindowGeometry(title)
            if not window_geometry:
                print(f"   ❌ 无法获取窗口几何信息: {title}")
                return None
            
            left, top, width, height = window_geometry
            left, top, width, height = int(left), int(top), int(width), int(height)
            
            if width < 300 or height < 400:
                print(f"   ❌ 窗口太小，跳过: {width}x{height}")
                return None
            
            print(f"🔍 分析窗口: '{title}' - {ScreenshotUtils.format_bounds_info({'x': left, 'y': top, 'width': width, 'height': height})}")
            
            # 截取窗口内容进行分析
            window_screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
            
            # 保存窗口截图用于调试
            safe_title = ScreenshotUtils.safe_filename(title)
            debug_path = ScreenshotUtils.save_debug_image(
                window_screenshot, 
                f"debug_window_{safe_title}.png", 
                "窗口截图"
            )
            
            # 转换为OpenCV格式分析
            screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
            
            # 使用分析器检测小程序特征区域
            miniprogram_bounds = self.analyzer.analyze_window_for_miniprogram(screenshot_cv, title)
            
            if miniprogram_bounds:
                # 转换为全局坐标
                global_bounds = {
                    'x': left + miniprogram_bounds['x'],
                    'y': top + miniprogram_bounds['y'],
                    'width': miniprogram_bounds['width'],
                    'height': miniprogram_bounds['height']
                }
                
                print(f"🎯 在窗口 '{title}' 中检测到小程序区域:")
                print(f"   局部坐标: {miniprogram_bounds}")
                print(f"   全局坐标: {global_bounds}")
                
                return global_bounds
                
        except Exception as e:
            print(f"⚠️ 分析窗口失败: {e}")
            return None 