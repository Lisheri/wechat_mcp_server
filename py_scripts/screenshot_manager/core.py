#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心截图管理器
整合所有子模块功能，提供统一的截图管理接口
"""

import os
import time
import pyautogui
from PIL import Image, ImageGrab
from config import CrawlerConfig
from .utils import ScreenshotUtils
from .detection_strategy import DetectionStrategy
from .validator import ScreenshotValidator


class ScreenshotManager:
    """核心截图管理器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.utils = ScreenshotUtils()
        self.detection_strategy = DetectionStrategy(window_manager)
        self.validator = ScreenshotValidator()
        
        # 为了向后兼容和测试，提供对各个检测器的直接访问
        self.system_detector = self.detection_strategy.system_detector
        self.edge_detector = self.detection_strategy.edge_detector
        self.content_detector = self.detection_strategy.content_detector
        
        # 确保截图目录存在
        os.makedirs(CrawlerConfig.SCREENSHOTS_DIR, exist_ok=True)
    
    def detect_mini_program_content_bounds(self):
        """智能检测小程序内容边界（多重检测策略）"""
        return self.detection_strategy.detect_miniprogram_bounds()
    
    def take_miniprogram_screenshot(self, filename="screenshot.png"):
        """拍摄小程序截图"""
        print(f"\n📸 开始拍摄小程序截图...")
        
        try:
            # 检测小程序区域
            bounds = self.detect_mini_program_content_bounds()
            if not bounds:
                print("❌ 无法检测到小程序区域")
                return None
            
            print(f"🎯 使用检测到的区域进行截图: {self.utils.format_bounds_info(bounds)}")
            
            # 拍摄截图（不再扩展边界，使用精确检测结果）
            screenshot = ImageGrab.grab(bbox=(
                bounds['x'],
                bounds['y'],
                bounds['x'] + bounds['width'],
                bounds['y'] + bounds['height']
            ))
            
            # 保存截图
            filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
            screenshot.save(filepath)
            print(f"📸 截图已保存: {filename}")
            
            # 自动验证截图质量
            self.validator.compare_screenshot_with_target(filepath)
            
            return filepath
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def take_scrolling_screenshot(self, title, scroll_pause_time=2, max_scrolls=10):
        """拍摄滚动截图"""
        print(f"\n📸 开始拍摄滚动截图: {title}")
        
        screenshots = []
        scroll_count = 0
        
        try:
            # 检测小程序区域
            bounds = self.detect_mini_program_content_bounds()
            if not bounds:
                print("❌ 无法检测到小程序区域，放弃滚动截图")
                return []
            
            # 计算滚动区域中心点
            center_point = self.utils.calculate_center_point(
                bounds['x'], bounds['y'], bounds['width'], bounds['height']
            )
            
            while scroll_count < max_scrolls:
                # 拍摄当前屏幕
                filename = f"{title}_scroll_{scroll_count + 1}.png"
                screenshot_path = self.take_miniprogram_screenshot(filename)
                
                if screenshot_path:
                    screenshots.append(screenshot_path)
                    print(f"✅ 滚动截图 {scroll_count + 1} 完成")
                else:
                    print(f"⚠️ 滚动截图 {scroll_count + 1} 失败")
                
                # 检查是否还有更多内容
                if scroll_count < max_scrolls - 1:
                    # 在小程序区域中心进行滚动
                    pyautogui.click(center_point['x'], center_point['y'])
                    time.sleep(0.3)
                    
                    # 向下滚动
                    pyautogui.scroll(-3, x=center_point['x'], y=center_point['y'])
                    time.sleep(scroll_pause_time)
                
                scroll_count += 1
            
            print(f"📸 滚动截图完成，共 {len(screenshots)} 张图片")
            return screenshots
            
        except Exception as e:
            print(f"❌ 滚动截图失败: {e}")
            import traceback
            traceback.print_exc()
            return screenshots 