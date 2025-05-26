#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图管理器
负责截图、滚动截图、图片处理等功能
"""

import os
import time
import pyautogui
import cv2
from PIL import Image
from skimage.metrics import structural_similarity as ssim
from config import CrawlerConfig

class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        
    def take_mini_program_screenshot(self, filename=None):
        """截取小程序区域的截图"""
        bounds = self.window_manager.get_mini_program_bounds()
        if not bounds:
            print("⚠️ 小程序区域未设置，无法截图")
            return None
        
        if filename is None:
            filename = CrawlerConfig.get_timestamp_filename("miniprogram")
        
        filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
        
        try:
            # 截取指定区域
            screenshot = pyautogui.screenshot(region=(
                bounds['x'], bounds['y'], 
                bounds['width'], bounds['height']
            ))
            
            screenshot.save(filepath)
            print(f"📸 小程序截图已保存: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def scroll_in_mini_program(self, direction='down', distance=None):
        """在小程序区域内滚动"""
        bounds = self.window_manager.get_mini_program_bounds()
        if not bounds:
            print("⚠️ 小程序区域未设置")
            return False
        
        if distance is None:
            distance = CrawlerConfig.SCROLL_DISTANCE
        
        # 在小程序区域中心滚动
        scroll_x = bounds['x'] + bounds['width'] // 2
        scroll_y = bounds['y'] + bounds['height'] // 2
        
        try:
            scroll_amount = distance if direction == 'down' else -distance
            pyautogui.scroll(-scroll_amount, x=scroll_x, y=scroll_y)
            time.sleep(CrawlerConfig.SCROLL_DELAY)
            return True
        except Exception as e:
            print(f"❌ 滚动失败: {e}")
            return False
    
    def take_full_page_screenshot(self):
        """滚动截取小程序的完整页面"""
        print("📜 开始滚动截取小程序完整页面...")
        
        # 确保聚焦到小程序
        self.window_manager.focus_mini_program_area()
        
        screenshots = []
        
        # 初始截图
        initial_screenshot = self.take_mini_program_screenshot("scroll_0.png")
        if not initial_screenshot:
            return None, []
        screenshots.append(initial_screenshot)
        
        # 滚动并截图
        for i in range(1, CrawlerConfig.MAX_SCROLLS + 1):
            # 向下滚动
            if not self.scroll_in_mini_program('down'):
                break
            
            # 截图
            scroll_screenshot = self.take_mini_program_screenshot(f"scroll_{i}.png")
            if not scroll_screenshot:
                break
            screenshots.append(scroll_screenshot)
            
            # 检查是否到达页面底部
            if i > 2 and self.are_screenshots_similar(screenshots[-1], screenshots[-2]):
                print(f"📄 检测到小程序页面底部，停止滚动 (滚动{i}次)")
                break
        
        # 拼接截图
        full_screenshot_path = self.stitch_screenshots(screenshots)
        if full_screenshot_path:
            print(f"🖼️ 小程序完整页面截图已生成: {os.path.basename(full_screenshot_path)}")
        
        return full_screenshot_path, screenshots
    
    def are_screenshots_similar(self, img1_path, img2_path):
        """比较两张截图的相似度"""
        try:
            img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                return False
            
            # 计算结构相似性
            similarity = ssim(img1, img2)
            return similarity > CrawlerConfig.SIMILARITY_THRESHOLD
            
        except Exception as e:
            print(f"⚠️ 截图相似度比较失败: {e}")
            return False
    
    def stitch_screenshots(self, screenshot_paths):
        """拼接多张截图为完整页面"""
        if not screenshot_paths:
            return None
            
        try:
            images = []
            for path in screenshot_paths:
                if os.path.exists(path):
                    images.append(Image.open(path))
            
            if not images:
                return None
            
            # 计算总高度
            total_height = sum(img.height for img in images)
            max_width = max(img.width for img in images)
            
            # 创建新图像
            stitched = Image.new('RGB', (max_width, total_height))
            
            # 拼接图像
            y_offset = 0
            for img in images:
                stitched.paste(img, (0, y_offset))
                y_offset += img.height
            
            # 保存拼接后的图像
            stitched_path = os.path.join(
                CrawlerConfig.SCREENSHOTS_DIR, 
                CrawlerConfig.get_timestamp_filename("full_page")
            )
            stitched.save(stitched_path)
            
            return stitched_path
            
        except Exception as e:
            print(f"❌ 截图拼接失败: {e}")
            return screenshot_paths[0] if screenshot_paths else None 