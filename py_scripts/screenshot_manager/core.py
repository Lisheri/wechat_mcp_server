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
        
        # 清理标志位，确保只在第一次激活时清理
        self._screenshots_cleaned = False
        
        # 为了向后兼容和测试，提供对各个检测器的直接访问
        self.system_detector = self.detection_strategy.system_detector
        self.edge_detector = self.detection_strategy.edge_detector
        self.content_detector = self.detection_strategy.content_detector
        
        # 确保截图目录存在
        os.makedirs(CrawlerConfig.SCREENSHOTS_DIR, exist_ok=True)
    
    def _clean_previous_screenshots(self):
        """清理上一轮的截图（只在第一次激活时执行）"""
        if not self._screenshots_cleaned:
            print("🗑️ 清理上一轮截图文件...")
            CrawlerConfig.clean_screenshots()
            self._screenshots_cleaned = True
    
    def start_screenshot_session(self):
        """启动截图会话，清理旧截图"""
        self._clean_previous_screenshots()
        print("📸 截图会话已启动")
    
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
        """拍摄滚动截图（优化版本）"""
        print(f"\n📸 开始拍摄滚动截图: {title}")
        
        screenshots = []
        scroll_count = 0
        previous_screenshot_hash = None
        
        try:
            # 检测小程序区域
            bounds = self.detect_mini_program_content_bounds()
            if not bounds:
                print("❌ 无法检测到小程序区域，放弃滚动截图")
                return []
            
            print(f"📐 小程序区域: {self.utils.format_bounds_info(bounds)}")
            
            # 计算安全的滚动区域（避免点击功能按钮）
            safe_scroll_point = self.utils.calculate_safe_scroll_point(
                bounds['x'], bounds['y'], bounds['width'], bounds['height']
            )
            
            # 计算动态滚动距离（窗口高度-40px）
            scroll_distance = max(3, (bounds['height'] - 40) // 100)  # 转换为滚动单位，最小为3
            print(f"📏 动态滚动距离: {scroll_distance} (基于窗口高度 {bounds['height']}px)")
            
            while scroll_count < max_scrolls:
                # 拍摄当前屏幕
                filename = f"{title}_scroll_{scroll_count + 1}.png"
                screenshot_path = self.take_miniprogram_screenshot(filename)
                
                if screenshot_path:
                    # 计算截图内容哈希，用于触底检测
                    current_hash = self._calculate_screenshot_hash(screenshot_path)
                    
                    # 检查是否触底（连续两次截图内容相同）
                    if previous_screenshot_hash and current_hash == previous_screenshot_hash:
                        print("🏁 检测到滚动触底，停止截图")
                        break
                    
                    screenshots.append(screenshot_path)
                    print(f"✅ 滚动截图 {scroll_count + 1} 完成")
                    previous_screenshot_hash = current_hash
                else:
                    print(f"⚠️ 滚动截图 {scroll_count + 1} 失败")
                
                # 检查是否还有更多内容
                if scroll_count < max_scrolls - 1:
                    # 在小程序安全区域进行滚动
                    print(f"📜 在安全区域滚动: ({safe_scroll_point['x']}, {safe_scroll_point['y']}) 距离: {scroll_distance}")
                    pyautogui.click(safe_scroll_point['x'], safe_scroll_point['y'])
                    time.sleep(0.3)
                    
                    # 向下滚动（使用动态距离）
                    pyautogui.scroll(-scroll_distance, x=safe_scroll_point['x'], y=safe_scroll_point['y'])
                    time.sleep(scroll_pause_time)
                
                scroll_count += 1
            
            # 滚动完成后，点击返回按钮回到上一页
            if screenshots:
                self._click_back_button(bounds)
            
            print(f"📸 滚动截图完成，共 {len(screenshots)} 张图片")
            return screenshots
            
        except Exception as e:
            print(f"❌ 滚动截图失败: {e}")
            import traceback
            traceback.print_exc()
            return screenshots
    
    def _calculate_screenshot_hash(self, screenshot_path):
        """计算截图内容哈希，用于触底检测"""
        try:
            import hashlib
            from PIL import Image
            
            # 打开图片并转换为灰度
            img = Image.open(screenshot_path).convert('L')
            
            # 缩小图片以提高比较速度
            img_resized = img.resize((64, 64))
            
            # 计算哈希值
            img_bytes = img_resized.tobytes()
            hash_value = hashlib.md5(img_bytes).hexdigest()
            
            return hash_value
            
        except Exception as e:
            print(f"⚠️ 计算截图哈希失败: {e}")
            return None
    
    def _click_back_button(self, bounds):
        """点击左上角返回按钮回到上一页"""
        try:
            # 计算左上角返回按钮位置
            # 通常在小程序左上角，距离边界约15-30像素
            back_button_x = bounds['x'] + 25  # 距离左边界25像素
            back_button_y = bounds['y'] + 35  # 距离顶部35像素
            
            print(f"🔙 点击返回按钮: ({back_button_x}, {back_button_y})")
            pyautogui.click(back_button_x, back_button_y)
            time.sleep(1.5)  # 等待页面切换
            
            print("✅ 已返回上一页")
            return True
            
        except Exception as e:
            print(f"⚠️ 点击返回按钮失败: {e}")
            return False 