#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交互管理器
负责小程序内的点击、返回等交互操作
"""

import time
import pyautogui
from config import CrawlerConfig

class InteractionManager:
    """交互管理器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
    
    def click_in_mini_program(self, relative_x, relative_y):
        """在小程序区域内点击指定相对坐标"""
        bounds = self.window_manager.get_mini_program_bounds()
        if not bounds:
            print("⚠️ 小程序区域未设置")
            return False
        
        # 转换为绝对坐标
        abs_x = bounds['x'] + relative_x
        abs_y = bounds['y'] + relative_y
        
        # 确保点击位置在小程序区域内
        if (0 <= relative_x <= bounds['width'] and 
            0 <= relative_y <= bounds['height']):
            try:
                pyautogui.click(abs_x, abs_y)
                time.sleep(CrawlerConfig.CLICK_DELAY)
                print(f"👆 在小程序内点击: 相对坐标({relative_x}, {relative_y}) -> 绝对坐标({abs_x}, {abs_y})")
                return True
            except Exception as e:
                print(f"❌ 点击操作失败: {e}")
                return False
        else:
            print(f"⚠️ 点击位置超出小程序区域: ({relative_x}, {relative_y})")
            return False
    
    def click_button(self, button_info):
        """点击指定按钮（在小程序区域内）"""
        try:
            # 使用相对坐标点击
            x, y = button_info['center_x'], button_info['center_y']
            print(f"🖱️ 点击按钮: {button_info['text']} 相对位置:({x}, {y})")
            
            # 使用小程序专用点击方法
            success = self.click_in_mini_program(x, y)
            if success:
                time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
                return True
            else:
                print(f"❌ 按钮点击失败: {button_info['text']}")
                return False
                
        except Exception as e:
            print(f"❌ 点击按钮异常: {e}")
            return False
    
    def go_back(self):
        """返回上一页（在小程序内）"""
        print("⬅️ 尝试返回上一页...")
        
        # 方法1: 尝试点击返回按钮（通常在左上角）
        for pos in CrawlerConfig.BACK_BUTTON_POSITIONS:
            print(f"🔙 尝试点击返回按钮位置: {pos}")
            if self.click_in_mini_program(pos[0], pos[1]):
                time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
                return True
        
        # 方法2: 使用手势滑动返回（从左边缘向右滑动）
        if self._try_swipe_back():
            return True
        
        # 方法3: 使用键盘ESC键
        if self._try_escape_back():
            return True
        
        print("❌ 所有返回方法都失败了")
        return False
    
    def _try_swipe_back(self):
        """尝试手势滑动返回"""
        try:
            bounds = self.window_manager.get_mini_program_bounds()
            if not bounds:
                return False
            
            start_x = bounds['x'] + 5
            start_y = bounds['y'] + bounds['height'] // 2
            end_x = start_x + 100
            end_y = start_y
            
            print(f"👈 尝试手势滑动返回: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
            pyautogui.drag(start_x, start_y, end_x, end_y, duration=0.5)
            time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
            return True
            
        except Exception as e:
            print(f"❌ 手势返回失败: {e}")
            return False
    
    def _try_escape_back(self):
        """尝试使用ESC键返回"""
        try:
            print("⌨️ 尝试使用ESC键返回")
            pyautogui.press('escape')
            time.sleep(CrawlerConfig.CLICK_DELAY)
            return True
        except Exception as e:
            print(f"❌ ESC键返回失败: {e}")
            return False
    
    def find_clickable_buttons(self, analysis_data):
        """从分析结果中找出可点击的按钮"""
        buttons = []
        
        if analysis_data and 'detectedButtons' in analysis_data:
            for button in analysis_data['detectedButtons']:
                pos = button.get('position', {})
                button_info = {
                    'text': button.get('text', ''),
                    'type': button.get('type', ''),
                    'x': pos.get('x', 0),
                    'y': pos.get('y', 0),
                    'width': pos.get('width', 0),
                    'height': pos.get('height', 0),
                    'center_x': pos.get('x', 0) + pos.get('width', 0) // 2,
                    'center_y': pos.get('y', 0) + pos.get('height', 0) // 2
                }
                buttons.append(button_info)
        
        return buttons 