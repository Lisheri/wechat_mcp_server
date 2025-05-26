#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口检测器
动态检测当前打开的小程序窗口位置和尺寸
支持通过小程序名称和激活状态进行精确检测
"""

import subprocess
import json
import re
import pyautogui
import cv2
import numpy as np
from PIL import Image
from typing import Optional, Dict, List

class WindowDetector:
    """窗口检测器类"""
    
    def __init__(self):
        self.current_mini_program_bounds = None
        self.current_app_name = None
        
    def detect_mini_program_window(self, app_name: str = None) -> Optional[Dict]:
        """
        检测当前打开的小程序窗口
        app_name: 小程序名称，用于验证是否为目标小程序
        返回窗口的位置和尺寸信息
        """
        print(f"🔍 正在检测小程序窗口{f': {app_name}' if app_name else ''}...")
        self.current_app_name = app_name
        
        # 方法1: 检测独立的小程序窗口（优先级最高）
        standalone_bounds = self._get_standalone_mini_program_bounds(app_name)
        if standalone_bounds:
            self.current_mini_program_bounds = standalone_bounds
            if app_name:
                print(f"✅ 检测到独立小程序窗口: {app_name}")
            else:
                print(f"✅ 检测到独立小程序窗口: {standalone_bounds}")
            return standalone_bounds
        
        # 方法2: 通过微信标题栏检测激活的小程序
        if app_name:
            wechat_bounds = self._get_wechat_window_bounds()
            if wechat_bounds and self._verify_mini_program_active(wechat_bounds, app_name):
                mini_program_bounds = self._calculate_mini_program_area(wechat_bounds)
                if mini_program_bounds:
                    self.current_mini_program_bounds = mini_program_bounds
                    print(f"✅ 检测到激活的小程序窗口: {app_name}")
                    print(f"📍 窗口位置: {mini_program_bounds}")
                    return mini_program_bounds
        
        # 方法3: 检测微信窗口中的小程序（通用方法）
        wechat_bounds = self._get_wechat_window_bounds()
        if wechat_bounds:
            mini_program_bounds = self._calculate_mini_program_area(wechat_bounds)
            if mini_program_bounds:
                self.current_mini_program_bounds = mini_program_bounds
                print(f"✅ 检测到小程序窗口: {mini_program_bounds}")
                return mini_program_bounds
        
        print("❌ 未能检测到小程序窗口")
        return None
    
    def _verify_mini_program_active(self, wechat_bounds: Dict, app_name: str) -> bool:
        """
        验证指定的小程序是否已激活
        通过检测微信标题栏中的小程序名称和激活状态指示器
        """
        print(f"🔍 验证小程序是否激活: {app_name}")
        
        try:
            # 截取微信窗口的标题栏区域
            title_bar_region = self._get_title_bar_region(wechat_bounds)
            if not title_bar_region:
                return False
            
            # 截取标题栏截图
            title_screenshot = pyautogui.screenshot(region=(
                title_bar_region['x'], title_bar_region['y'],
                title_bar_region['width'], title_bar_region['height']
            ))
            
            # 检测红框中的文案
            app_name_detected = self._detect_app_name_in_title(title_screenshot, app_name)
            
            # 检测右侧的激活状态指示器（小圆点）
            active_indicator_detected = self._detect_active_indicator(title_screenshot)
            
            if app_name_detected and active_indicator_detected:
                print(f"✅ 小程序 '{app_name}' 已激活并检测到状态指示器")
                return True
            elif app_name_detected:
                print(f"⚠️ 检测到小程序名称 '{app_name}' 但未发现激活状态指示器")
                return True  # 即使没有检测到指示器，如果名称匹配也认为是激活的
            else:
                print(f"❌ 未检测到小程序 '{app_name}' 或其激活状态")
                return False
                
        except Exception as e:
            print(f"⚠️ 验证小程序激活状态失败: {e}")
            return False
    
    def _get_title_bar_region(self, wechat_bounds: Dict) -> Optional[Dict]:
        """获取微信窗口标题栏区域"""
        # 标题栏通常在窗口顶部，高度约为40-80像素
        title_height = 80
        return {
            'x': wechat_bounds['x'],
            'y': wechat_bounds['y'],
            'width': wechat_bounds['width'],
            'height': title_height
        }
    
    def _detect_app_name_in_title(self, title_screenshot: Image.Image, app_name: str) -> bool:
        """
        在标题栏截图中检测小程序名称
        使用图像处理和文字识别技术
        """
        try:
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(title_screenshot), cv2.COLOR_RGB2BGR)
            
            # 转换为灰度图
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 检测红色框区域（假设小程序名称在红色框中）
            red_regions = self._detect_red_frame_regions(cv_image)
            
            if red_regions:
                # 在红色框区域中查找文字
                for region in red_regions:
                    x, y, w, h = region
                    roi = gray[y:y+h, x:x+w]
                    
                    # 使用简单的文字检测（这里可以集成OCR库如tesseract）
                    if self._contains_text_pattern(roi, app_name):
                        print(f"✅ 在红框中检测到小程序名称: {app_name}")
                        return True
            
            # 如果没有检测到红框，尝试在整个标题栏中查找
            if self._contains_text_pattern(gray, app_name):
                print(f"✅ 在标题栏中检测到小程序名称: {app_name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 检测小程序名称失败: {e}")
            return False
    
    def _detect_red_frame_regions(self, cv_image) -> List:
        """检测图像中的红色框区域"""
        try:
            # 转换到HSV色彩空间
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # 定义红色的HSV范围
            lower_red1 = np.array([0, 50, 50])
            upper_red1 = np.array([10, 255, 255])
            lower_red2 = np.array([170, 50, 50])
            upper_red2 = np.array([180, 255, 255])
            
            # 创建红色掩码
            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            regions = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # 过滤太小的区域
                if w > 50 and h > 20:
                    regions.append((x, y, w, h))
            
            return regions
            
        except Exception as e:
            print(f"⚠️ 检测红色框失败: {e}")
            return []
    
    def _detect_active_indicator(self, title_screenshot: Image.Image) -> bool:
        """
        检测激活状态指示器（右侧小圆点）
        """
        try:
            # 转换为OpenCV格式
            cv_image = cv2.cvtColor(np.array(title_screenshot), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
            
            # 在图像右侧区域查找圆形
            height, width = gray.shape
            right_region = gray[:, int(width * 0.7):]  # 只检查右侧30%的区域
            
            # 使用霍夫圆检测
            circles = cv2.HoughCircles(
                right_region,
                cv2.HOUGH_GRADIENT,
                dp=1,
                minDist=10,
                param1=50,
                param2=15,
                minRadius=3,
                maxRadius=15
            )
            
            if circles is not None:
                circles = np.round(circles[0, :]).astype("int")
                if len(circles) > 0:
                    print(f"✅ 检测到 {len(circles)} 个可能的激活状态指示器")
                    return True
            
            # 备用方法：检测特定颜色的小圆点
            return self._detect_colored_dots(cv_image)
            
        except Exception as e:
            print(f"⚠️ 检测激活状态指示器失败: {e}")
            return False
    
    def _detect_colored_dots(self, cv_image) -> bool:
        """检测彩色小圆点（绿色、橙色等）"""
        try:
            hsv = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
            
            # 定义绿色和橙色的HSV范围（常见的激活状态指示器颜色）
            color_ranges = [
                # 绿色
                ([40, 50, 50], [80, 255, 255]),
                # 橙色
                ([10, 50, 50], [25, 255, 255]),
                # 蓝色
                ([100, 50, 50], [130, 255, 255])
            ]
            
            height, width = cv_image.shape[:2]
            right_region = cv_image[:, int(width * 0.7):]  # 只检查右侧区域
            right_hsv = cv2.cvtColor(right_region, cv2.COLOR_BGR2HSV)
            
            for lower, upper in color_ranges:
                mask = cv2.inRange(right_hsv, np.array(lower), np.array(upper))
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    area = cv2.contourArea(contour)
                    if 10 < area < 200:  # 小圆点的面积范围
                        print("✅ 检测到彩色状态指示器")
                        return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 检测彩色圆点失败: {e}")
            return False
    
    def _contains_text_pattern(self, gray_image, app_name: str) -> bool:
        """
        简单的文字模式匹配
        这里使用基础的图像处理方法，实际项目中可以集成OCR库
        """
        try:
            # 应用阈值处理
            _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 查找轮廓（文字区域）
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 统计可能的文字区域数量
            text_regions = 0
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                # 文字区域的典型特征：宽高比合理，面积适中
                if 5 < w < 100 and 8 < h < 30 and 0.2 < w/h < 5:
                    text_regions += 1
            
            # 如果检测到足够的文字区域，认为可能包含目标文字
            # 这是一个简化的实现，实际应该使用OCR
            expected_chars = len(app_name)
            if text_regions >= expected_chars * 0.5:  # 至少检测到一半的字符
                return True
            
            return False
            
        except Exception as e:
            print(f"⚠️ 文字模式匹配失败: {e}")
            return False
    
    def _get_wechat_window_bounds(self) -> Optional[Dict]:
        """获取微信主窗口的位置和尺寸"""
        try:
            script = '''
            tell application "System Events"
                set wechatApp to first application process whose name is "WeChat"
                set wechatWindows to windows of wechatApp
                
                if (count of wechatWindows) > 0 then
                    set mainWin to first window of wechatApp
                    set winPosition to position of mainWin
                    set winSize to size of mainWin
                    
                    return (item 1 of winPosition) & "," & (item 2 of winPosition) & "," & (item 1 of winSize) & "," & (item 2 of winSize)
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                coords = result.stdout.strip().split(',')
                if len(coords) == 4:
                    return {
                        'x': int(coords[0]),
                        'y': int(coords[1]),
                        'width': int(coords[2]),
                        'height': int(coords[3])
                    }
        except Exception as e:
            print(f"⚠️ 获取微信窗口信息失败: {e}")
        
        return None
    
    def _calculate_mini_program_area(self, wechat_bounds: Dict) -> Optional[Dict]:
        """
        根据微信窗口计算小程序区域
        这里使用一些启发式规则来估算小程序在微信窗口中的位置
        """
        # 微信窗口的典型布局：
        # - 顶部标题栏: ~40px
        # - 左侧聊天列表: ~300px (如果是双栏布局)
        # - 小程序区域: 剩余区域
        
        # 检查是否是单栏布局（窗口较窄）还是双栏布局（窗口较宽）
        if wechat_bounds['width'] < 600:
            # 单栏布局，小程序占据大部分区域
            mini_program_x = wechat_bounds['x'] + 10
            mini_program_y = wechat_bounds['y'] + 80  # 跳过标题栏和导航
            mini_program_width = wechat_bounds['width'] - 20
            mini_program_height = wechat_bounds['height'] - 120
        else:
            # 双栏布局，小程序在右侧
            mini_program_x = wechat_bounds['x'] + 300  # 跳过左侧聊天列表
            mini_program_y = wechat_bounds['y'] + 80
            mini_program_width = wechat_bounds['width'] - 320
            mini_program_height = wechat_bounds['height'] - 120
        
        # 确保尺寸合理
        if mini_program_width > 100 and mini_program_height > 100:
            return {
                'x': mini_program_x,
                'y': mini_program_y,
                'width': mini_program_width,
                'height': mini_program_height
            }
        
        return None
    
    def _get_standalone_mini_program_bounds(self, app_name: str = None) -> Optional[Dict]:
        """检测独立的小程序窗口"""
        try:
            if app_name:
                # 方法1: 在Mini Program进程中查找指定名称的窗口
                script = f'''
                tell application "System Events"
                    try
                        set miniProgramApp to application process "Mini Program"
                        set targetWindow to window "{app_name}" of miniProgramApp
                        set winPosition to position of targetWindow
                        set winSize to size of targetWindow
                        
                        set x to item 1 of winPosition as string
                        set y to item 2 of winPosition as string
                        set w to item 1 of winSize as string
                        set h to item 2 of winSize as string
                        
                        return x & "," & y & "," & w & "," & h
                    on error
                        return ""
                    end try
                end tell
                '''
                
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    coords = result.stdout.strip().split(',')
                    if len(coords) == 4:
                        print(f"✅ 在Mini Program进程中找到小程序: {app_name}")
                        return {
                            'x': int(coords[0]),
                            'y': int(coords[1]),
                            'width': int(coords[2]),
                            'height': int(coords[3])
                        }
                
                # 方法2: 在所有进程中查找包含该名称的窗口
                script = f'''
                tell application "System Events"
                    set allApps to every application process
                    repeat with app in allApps
                        set appName to name of app
                        try
                            set appWindows to windows of app
                            repeat with win in appWindows
                                set winTitle to title of win
                                if winTitle contains "{app_name}" then
                                    set winPosition to position of win
                                    set winSize to size of win
                                    
                                    set x to item 1 of winPosition as string
                                    set y to item 2 of winPosition as string
                                    set w to item 1 of winSize as string
                                    set h to item 2 of winSize as string
                                    
                                    return x & "," & y & "," & w & "," & h
                                end if
                            end repeat
                        on error
                            -- 忽略无法访问的应用
                        end try
                    end repeat
                    return ""
                end tell
                '''
            else:
                # 通用查找小程序窗口
                script = '''
                tell application "System Events"
                    set allApps to every application process
                    repeat with app in allApps
                        set appName to name of app
                        if appName contains "小程序" or appName contains "Mini Program" then
                            try
                                set appWindows to windows of app
                                if (count of appWindows) > 0 then
                                    set mainWin to first window of app
                                    set winPosition to position of mainWin
                                    set winSize to size of mainWin
                                    
                                    set x to item 1 of winPosition as string
                                    set y to item 2 of winPosition as string
                                    set w to item 1 of winSize as string
                                    set h to item 2 of winSize as string
                                    
                                    return x & "," & y & "," & w & "," & h
                                end if
                            on error
                                -- 忽略无法访问的应用
                            end try
                        end if
                    end repeat
                    return ""
                end tell
                '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                coords = result.stdout.strip().split(',')
                if len(coords) == 4:
                    return {
                        'x': int(coords[0]),
                        'y': int(coords[1]),
                        'width': int(coords[2]),
                        'height': int(coords[3])
                    }
        except Exception as e:
            print(f"⚠️ 检测独立小程序窗口失败: {e}")
        
        return None
    
    def get_current_bounds(self) -> Optional[Dict]:
        """获取当前检测到的小程序窗口边界"""
        return self.current_mini_program_bounds
    
    def refresh_detection(self) -> Optional[Dict]:
        """刷新窗口检测"""
        return self.detect_mini_program_window()
    
    def get_center_point(self) -> Optional[tuple]:
        """获取小程序窗口的中心点坐标"""
        if not self.current_mini_program_bounds:
            return None
        
        bounds = self.current_mini_program_bounds
        center_x = bounds['x'] + bounds['width'] // 2
        center_y = bounds['y'] + bounds['height'] // 2
        
        return (center_x, center_y)
    
    def is_point_in_mini_program(self, x: int, y: int) -> bool:
        """检查指定点是否在小程序窗口内"""
        if not self.current_mini_program_bounds:
            return False
        
        bounds = self.current_mini_program_bounds
        return (bounds['x'] <= x <= bounds['x'] + bounds['width'] and
                bounds['y'] <= y <= bounds['y'] + bounds['height']) 