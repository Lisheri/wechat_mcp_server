#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信窗口管理器
负责微信窗口的查找、聚焦和小程序入口处理
"""

import subprocess
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageGrab
from config import CrawlerConfig

class WeChatWindowManager:
    """微信窗口管理器"""
    
    def __init__(self):
        self.mini_program_bounds = None
        self.is_in_mini_program = False
        self.wechat_window_bounds = None
        
    def find_and_setup_wechat_window(self):
        """查找并设置微信窗口"""
        print("🔍 正在查找微信窗口...")
        
        try:
            # 使用AppleScript查找并设置微信窗口
            script = f'''
            tell application "System Events"
                set wechatApp to first application process whose name is "WeChat"
                set wechatWindows to windows of wechatApp
                
                if (count of wechatWindows) > 0 then
                    set mainWin to first window of wechatApp
                    set position of mainWin to {{{CrawlerConfig.WECHAT_WINDOW_POSITION[0]}, {CrawlerConfig.WECHAT_WINDOW_POSITION[1]}}}
                    set size of mainWin to {{{CrawlerConfig.WECHAT_WINDOW_SIZE[0]}, {CrawlerConfig.WECHAT_WINDOW_SIZE[1]}}}
                    tell application "WeChat" to activate
                    set frontmost of wechatApp to true
                    return "success"
                end if
            end tell
            '''
            
            result = subprocess.run(['osascript', '-e', script], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and "success" in result.stdout:
                print("✅ 微信窗口设置成功")
                time.sleep(2)  # 等待窗口调整完成
                
                # 记录微信窗口边界
                self.wechat_window_bounds = {
                    'x': CrawlerConfig.WECHAT_WINDOW_POSITION[0],
                    'y': CrawlerConfig.WECHAT_WINDOW_POSITION[1],
                    'width': CrawlerConfig.WECHAT_WINDOW_SIZE[0],
                    'height': CrawlerConfig.WECHAT_WINDOW_SIZE[1]
                }
                
                return True
            else:
                print(f"❌ 微信窗口设置失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 查找微信窗口失败: {e}")
            return False
    
    def detect_mini_program_area(self):
        """动态检测小程序区域"""
        print("🔍 正在动态检测小程序区域...")
        
        if not self.wechat_window_bounds:
            print("❌ 微信窗口未初始化")
            return False
        
        try:
            # 截取微信窗口
            screenshot = ImageGrab.grab(bbox=(
                self.wechat_window_bounds['x'],
                self.wechat_window_bounds['y'],
                self.wechat_window_bounds['x'] + self.wechat_window_bounds['width'],
                self.wechat_window_bounds['y'] + self.wechat_window_bounds['height']
            ))
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 检测是否已经在小程序界面
            if self.is_already_in_mini_program(screenshot_cv):
                print("✅ 检测到已在小程序界面")
                self.is_in_mini_program = True
                # 设置整个微信窗口为小程序区域（去掉顶部标题栏）
                self.mini_program_bounds = {
                    'x': 0,
                    'y': 30,  # 跳过标题栏
                    'width': self.wechat_window_bounds['width'],
                    'height': self.wechat_window_bounds['height'] - 30
                }
                return True
            
            # 检测小程序入口按钮
            mini_program_button = self.find_mini_program_button(screenshot_cv)
            if mini_program_button:
                print(f"✅ 找到小程序入口按钮: {mini_program_button}")
                return True
            
            print("⚠️ 未检测到小程序相关界面")
            return False
            
        except Exception as e:
            print(f"❌ 检测小程序区域失败: {e}")
            return False
    
    def is_already_in_mini_program(self, screenshot):
        """检测是否已经在小程序界面"""
        # 转换为灰度图
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # 检测小程序界面的特征
        # 1. 检测顶部导航栏（通常有返回按钮）
        top_region = gray[0:60, :]
        
        # 使用边缘检测寻找返回按钮
        edges = cv2.Canny(top_region, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 如果顶部有小的矩形区域（可能是返回按钮），认为在小程序内
        for contour in contours:
            area = cv2.contourArea(contour)
            if 100 < area < 2000:  # 返回按钮的大概面积
                x, y, w, h = cv2.boundingRect(contour)
                if w > 10 and h > 10 and x < 100:  # 返回按钮通常在左上角
                    return True
        
        # 2. 检测是否有小程序特有的UI元素（如底部导航栏）
        bottom_region = gray[-100:, :]
        bottom_edges = cv2.Canny(bottom_region, 50, 150)
        
        # 如果底部有水平线条，可能是小程序的底部导航
        horizontal_lines = cv2.HoughLinesP(bottom_edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
        if horizontal_lines is not None and len(horizontal_lines) > 0:
            return True
        
        return False
    
    def find_mini_program_button(self, screenshot):
        """查找小程序入口按钮"""
        # 转换为HSV颜色空间，便于检测特定颜色
        hsv = cv2.cvtColor(screenshot, cv2.COLOR_BGR2HSV)
        
        # 检测可能的小程序按钮（通常是圆角矩形，有特定颜色）
        # 这里可以根据实际的小程序按钮颜色调整
        
        # 检测底部导航区域
        height = screenshot.shape[0]
        bottom_region = screenshot[int(height * 0.8):, :]  # 底部20%区域
        
        # 转换为灰度图进行轮廓检测
        gray_bottom = cv2.cvtColor(bottom_region, cv2.COLOR_BGR2GRAY)
        
        # 使用自适应阈值
        thresh = cv2.adaptiveThreshold(gray_bottom, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 寻找可能的按钮
        for contour in contours:
            area = cv2.contourArea(contour)
            if 500 < area < 5000:  # 按钮的大概面积
                x, y, w, h = cv2.boundingRect(contour)
                # 调整坐标到整个截图的坐标系
                actual_y = int(height * 0.8) + y
                
                # 检查长宽比，按钮通常接近正方形或稍微宽一些
                aspect_ratio = w / h
                if 0.5 < aspect_ratio < 2.0:
                    button_center = (
                        self.wechat_window_bounds['x'] + x + w//2,
                        self.wechat_window_bounds['y'] + actual_y + h//2
                    )
                    return button_center
        
        return None
    
    def click_mini_program_entry(self):
        """智能点击小程序入口"""
        print("📱 正在智能检测并点击小程序入口...")
        
        # 先检测当前状态
        if not self.detect_mini_program_area():
            print("❌ 无法检测到小程序相关界面")
            return False
        
        # 如果已经在小程序内，直接返回成功
        if self.is_in_mini_program:
            print("✅ 已在小程序界面，无需点击入口")
            return True
        
        # 尝试多种方式找到小程序入口
        entry_positions = [
            # 常见的小程序入口位置（相对于微信窗口）
            (self.wechat_window_bounds['x'] + 50, self.wechat_window_bounds['y'] + self.wechat_window_bounds['height'] - 100),
            (self.wechat_window_bounds['x'] + 100, self.wechat_window_bounds['y'] + self.wechat_window_bounds['height'] - 80),
            (self.wechat_window_bounds['x'] + 30, self.wechat_window_bounds['y'] + self.wechat_window_bounds['height'] - 120),
        ]
        
        for pos in entry_positions:
            try:
                print(f"🎯 尝试点击位置: {pos}")
                pyautogui.click(pos[0], pos[1])
                time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
                
                # 检测是否成功进入小程序界面
                if self.detect_mini_program_area():
                    print("✅ 成功进入小程序界面")
                    return True
                    
            except Exception as e:
                print(f"⚠️ 点击位置 {pos} 失败: {e}")
                continue
        
        print("❌ 所有尝试都失败，无法进入小程序")
        return False
    
    def select_first_mini_program(self):
        """智能选择第一个小程序"""
        print("🎯 正在智能选择小程序...")
        
        if self.is_in_mini_program:
            print("✅ 已在小程序界面")
            return True
        
        try:
            # 截取当前屏幕
            screenshot = ImageGrab.grab(bbox=(
                self.wechat_window_bounds['x'],
                self.wechat_window_bounds['y'],
                self.wechat_window_bounds['x'] + self.wechat_window_bounds['width'],
                self.wechat_window_bounds['y'] + self.wechat_window_bounds['height']
            ))
            
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 查找小程序图标（通常是圆角矩形）
            mini_programs = self.find_mini_program_icons(screenshot_cv)
            
            if mini_programs:
                # 选择第一个小程序
                first_program = mini_programs[0]
                click_x = self.wechat_window_bounds['x'] + first_program[0]
                click_y = self.wechat_window_bounds['y'] + first_program[1]
                
                print(f"🎯 点击第一个小程序: ({click_x}, {click_y})")
                pyautogui.click(click_x, click_y)
                time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
                
                self.is_in_mini_program = True
                print("✅ 已进入小程序")
                return True
            else:
                print("❌ 未找到小程序图标")
                return False
                
        except Exception as e:
            print(f"❌ 选择小程序失败: {e}")
            return False
    
    def find_mini_program_icons(self, screenshot):
        """查找小程序图标"""
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # 使用模板匹配或轮廓检测找到小程序图标
        # 小程序图标通常是圆角矩形，大小相似
        
        # 使用边缘检测
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        icons = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if 1000 < area < 10000:  # 小程序图标的大概面积
                x, y, w, h = cv2.boundingRect(contour)
                
                # 检查长宽比，小程序图标通常接近正方形
                aspect_ratio = w / h
                if 0.8 < aspect_ratio < 1.2 and w > 30 and h > 30:
                    # 返回图标中心点
                    center_x = x + w // 2
                    center_y = y + h // 2
                    icons.append((center_x, center_y))
        
        # 按位置排序（从上到下，从左到右）
        icons.sort(key=lambda icon: (icon[1], icon[0]))
        return icons
    
    def focus_mini_program_area(self):
        """聚焦到小程序区域（点击顶部安全区域）"""
        if not self.mini_program_bounds:
            print("⚠️ 小程序区域未设置，使用默认区域")
            # 使用整个微信窗口作为小程序区域
            self.mini_program_bounds = {
                'x': 0,
                'y': 30,
                'width': self.wechat_window_bounds['width'],
                'height': self.wechat_window_bounds['height'] - 30
            }
        
        # 计算小程序顶部安全区域的中心点（避免点击功能按钮）
        # 顶部区域通常是标题栏或导航栏，相对安全
        safe_top_area_height = 50  # 顶部安全区域高度
        
        center_x = (self.wechat_window_bounds['x'] + 
                   self.mini_program_bounds['x'] + 
                   self.mini_program_bounds['width'] // 2)
        # 点击顶部安全区域，距离顶部25像素的位置
        safe_y = (self.wechat_window_bounds['y'] + 
                 self.mini_program_bounds['y'] + 
                 safe_top_area_height // 2)
        
        try:
            print(f"🎯 聚焦到小程序顶部安全区域: ({center_x}, {safe_y})")
            pyautogui.click(center_x, safe_y)
            time.sleep(CrawlerConfig.FOCUS_DELAY)
            print("✅ 已安全聚焦到小程序顶部区域")
            return True
        except Exception as e:
            print(f"❌ 聚焦失败: {e}")
            return False
    
    def get_mini_program_bounds(self):
        """获取小程序区域边界"""
        if not self.mini_program_bounds or not self.wechat_window_bounds:
            return None
        
        return {
            'x': self.wechat_window_bounds['x'] + self.mini_program_bounds['x'],
            'y': self.wechat_window_bounds['y'] + self.mini_program_bounds['y'],
            'width': self.mini_program_bounds['width'],
            'height': self.mini_program_bounds['height']
        }
    
    def setup_mini_program_environment(self):
        """设置小程序环境（完整流程）"""
        print("🚀 开始设置小程序环境...")
        
        # 1. 查找并设置微信窗口
        if not self.find_and_setup_wechat_window():
            return False
        
        # 2. 动态检测小程序区域
        if not self.detect_mini_program_area():
            print("⚠️ 尝试点击小程序入口...")
            # 3. 如果不在小程序界面，尝试点击入口
            if not self.click_mini_program_entry():
                return False
        
        # 4. 如果还不在小程序内，尝试选择第一个小程序
        if not self.is_in_mini_program:
            if not self.select_first_mini_program():
                return False
        
        # 5. 聚焦到小程序区域
        if not self.focus_mini_program_area():
            return False
        
        print("✅ 小程序环境设置完成")
        return True 