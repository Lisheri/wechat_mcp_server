#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图工具类
包含通用的工具函数和辅助方法
"""

import os
import time
import numpy as np
from PIL import Image, ImageGrab
from config import CrawlerConfig


class ScreenshotUtils:
    """截图工具类"""
    
    @staticmethod
    def clean_old_screenshots():
        """清理旧的截图文件"""
        if os.path.exists(CrawlerConfig.SCREENSHOTS_DIR):
            for filename in os.listdir(CrawlerConfig.SCREENSHOTS_DIR):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 已删除旧截图: {filename}")
                    except Exception as e:
                        print(f"⚠️ 删除截图失败: {filename} - {e}")
    
    @staticmethod
    def take_debug_screenshot(filename="debug.png"):
        """拍摄调试截图，显示当前整个屏幕状态"""
        try:
            filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            print(f"🐛 调试截图已保存: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ 调试截图失败: {e}")
            return None
    
    @staticmethod
    def expand_screenshot_bounds(bounds, expansion_x=5, expansion_y=5):
        """轻微扩展截图边界以确保完整覆盖"""
        import pyautogui
        
        expanded = {
            'x': max(0, bounds['x'] - expansion_x),
            'y': max(0, bounds['y'] - expansion_y),
            'width': bounds['width'] + 2 * expansion_x,
            'height': bounds['height'] + 2 * expansion_y
        }
        
        # 确保不超出屏幕边界
        screen_width, screen_height = pyautogui.size()
        if expanded['x'] + expanded['width'] > screen_width:
            expanded['width'] = screen_width - expanded['x']
        if expanded['y'] + expanded['height'] > screen_height:
            expanded['height'] = screen_height - expanded['y']
        
        print(f"📐 轻微扩展截图区域: 原始{bounds['width']}x{bounds['height']} -> 扩展{expanded['width']}x{expanded['height']}")
        return expanded
    
    @staticmethod
    def save_debug_image(image, filename, description=""):
        """保存调试图像"""
        try:
            filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
            if isinstance(image, np.ndarray):
                import cv2
                cv2.imwrite(filepath, image)
            else:
                image.save(filepath)
            print(f"🐛 {description}已保存: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ 保存调试图像失败: {e}")
            return None
    
    @staticmethod
    def safe_filename(title):
        """生成安全的文件名"""
        return title.replace('/', '_').replace(':', '_').replace('\\', '_').replace('?', '_').replace('*', '_')
    
    @staticmethod
    def calculate_aspect_ratio(width, height):
        """计算长宽比"""
        return height / width if width > 0 else 0
    
    @staticmethod
    def is_size_in_range(width, height, min_width=300, max_width=600, min_height=400, max_height=900):
        """检查尺寸是否在合理范围内"""
        return (min_width <= width <= max_width and 
                min_height <= height <= max_height)
    
    @staticmethod
    def calculate_center_point(x, y, width, height):
        """计算区域中心点"""
        return {
            'x': x + width // 2,
            'y': y + height // 2
        }
    
    @staticmethod
    def format_bounds_info(bounds):
        """格式化边界信息输出"""
        return f"位置({bounds['x']},{bounds['y']}) 尺寸({bounds['width']}x{bounds['height']})" 