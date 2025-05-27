#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮导航器
负责按钮点击和页面导航管理
"""

import time
import pyautogui
from config import CrawlerConfig


class ButtonNavigator:
    """按钮导航器类"""
    
    def __init__(self, window_manager):
        """初始化按钮导航器"""
        self.window_manager = window_manager
        self.navigation_history = []
        self.current_page = "主页"
    
    def click_button(self, button, bounds):
        """点击指定按钮"""
        try:
            # 获取按钮的绝对点击位置
            center_x, center_y = button['center']
            absolute_x = bounds['x'] + center_x
            absolute_y = bounds['y'] + center_y
            
            print(f"🎯 点击按钮: {button['target']} 位置: ({absolute_x}, {absolute_y})")
            
            # 确保聚焦到小程序区域
            self.window_manager.focus_mini_program_area()
            time.sleep(0.5)
            
            # 点击按钮
            pyautogui.click(absolute_x, absolute_y)
            time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
            
            # 记录导航历史
            self.navigation_history.append({
                'from_page': self.current_page,
                'to_page': button['target'],
                'button': button,
                'timestamp': time.time()
            })
            
            self.current_page = button['target']
            print(f"✅ 成功进入: {button['target']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 点击按钮失败: {e}")
            return False
    
    def return_to_main_page(self, bounds):
        """返回主页面"""
        try:
            # 计算返回按钮位置（左上角）
            back_x = bounds['x'] + 25
            back_y = bounds['y'] + 35
            
            print(f"🔙 点击返回按钮返回主页: ({back_x}, {back_y})")
            
            # 确保聚焦到小程序区域
            self.window_manager.focus_mini_program_area()
            time.sleep(0.5)
            
            # 点击返回按钮
            pyautogui.click(back_x, back_y)
            time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
            
            # 更新当前页面状态
            self.current_page = "主页"
            
            print("✅ 已返回主页")
            return True
            
        except Exception as e:
            print(f"❌ 返回主页失败: {e}")
            return False
    
    def get_current_page(self):
        """获取当前页面名称"""
        return self.current_page
    
    def is_on_main_page(self):
        """检查是否在主页"""
        return self.current_page == "主页"
    
    def get_navigation_history(self):
        """获取导航历史"""
        return self.navigation_history
    
    def clear_navigation_history(self):
        """清空导航历史"""
        self.navigation_history = []
        self.current_page = "主页"
        print("🔄 已清空导航历史")
    
    def get_last_visited_button(self):
        """获取最后访问的按钮"""
        if not self.navigation_history:
            return None
        
        return self.navigation_history[-1]
    
    def ensure_main_page(self, bounds, max_attempts=3):
        """确保回到主页面"""
        attempt = 0
        
        while attempt < max_attempts:
            if self.is_on_main_page():
                print("✅ 已在主页")
                return True
            
            attempt += 1
            print(f"🔄 尝试返回主页 (第{attempt}次)")
            
            if self.return_to_main_page(bounds):
                time.sleep(1)  # 等待页面加载
            else:
                print(f"⚠️ 第{attempt}次返回失败")
        
        print("❌ 无法确保返回主页")
        return False
    
    def navigate_to_button_page(self, button, bounds):
        """导航到指定按钮页面"""
        print(f"🧭 导航到页面: {button['target']}")
        
        # 如果不在主页，先返回主页
        if not self.is_on_main_page():
            if not self.ensure_main_page(bounds):
                return False
        
        # 点击目标按钮
        if self.click_button(button, bounds):
            return True
        else:
            print(f"❌ 导航到 {button['target']} 失败")
            return False
    
    def get_navigation_summary(self):
        """获取导航摘要"""
        total_navigations = len(self.navigation_history)
        unique_pages = set([nav['to_page'] for nav in self.navigation_history])
        
        return {
            'current_page': self.current_page,
            'total_navigations': total_navigations,
            'unique_pages_visited': len(unique_pages),
            'pages_visited': list(unique_pages)
        } 