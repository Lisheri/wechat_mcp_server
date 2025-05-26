#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信窗口管理器
负责微信窗口的查找、聚焦和小程序入口处理
"""

import subprocess
import time
import pyautogui
from config import CrawlerConfig

class WeChatWindowManager:
    """微信窗口管理器"""
    
    def __init__(self):
        self.mini_program_bounds = None
        self.is_in_mini_program = False
        
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
                
                # 设置小程序区域
                self.mini_program_bounds = CrawlerConfig.MINI_PROGRAM_BOUNDS.copy()
                return True
            else:
                print(f"❌ 微信窗口设置失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 查找微信窗口失败: {e}")
            return False
    
    def click_mini_program_entry(self):
        """点击小程序入口按钮"""
        print("📱 正在点击小程序入口...")
        
        if not self.mini_program_bounds:
            print("❌ 微信窗口未初始化")
            return False
        
        # 点击小程序入口（通常在微信主界面的底部导航）
        entry_x = CrawlerConfig.WECHAT_WINDOW_POSITION[0] + 30  # 小程序图标位置
        entry_y = CrawlerConfig.WECHAT_WINDOW_POSITION[1] + 650  # 底部导航位置
        
        try:
            pyautogui.click(entry_x, entry_y)
            time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
            print("✅ 已点击小程序入口")
            return True
        except Exception as e:
            print(f"❌ 点击小程序入口失败: {e}")
            return False
    
    def select_first_mini_program(self):
        """选择第一个小程序或聚焦到当前小程序"""
        print("🎯 正在选择小程序...")
        
        if not self.mini_program_bounds:
            print("❌ 微信窗口未初始化")
            return False
        
        # 计算第一个小程序的位置（基于您提供的截图）
        first_program_x = CrawlerConfig.WECHAT_WINDOW_POSITION[0] + CrawlerConfig.MINI_PROGRAM_ENTRY_BOUNDS['x']
        first_program_y = CrawlerConfig.WECHAT_WINDOW_POSITION[1] + CrawlerConfig.MINI_PROGRAM_ENTRY_BOUNDS['y']
        
        try:
            # 点击第一个小程序
            pyautogui.click(first_program_x, first_program_y)
            time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
            
            # 更新状态
            self.is_in_mini_program = True
            print("✅ 已进入小程序")
            return True
            
        except Exception as e:
            print(f"❌ 选择小程序失败: {e}")
            return False
    
    def focus_mini_program_area(self):
        """聚焦到小程序区域"""
        if not self.mini_program_bounds:
            print("⚠️ 小程序区域未设置")
            return False
        
        # 计算小程序区域中心点
        center_x = (CrawlerConfig.WECHAT_WINDOW_POSITION[0] + 
                   self.mini_program_bounds['x'] + 
                   self.mini_program_bounds['width'] // 2)
        center_y = (CrawlerConfig.WECHAT_WINDOW_POSITION[1] + 
                   self.mini_program_bounds['y'] + 
                   self.mini_program_bounds['height'] // 2)
        
        try:
            pyautogui.click(center_x, center_y)
            time.sleep(CrawlerConfig.FOCUS_DELAY)
            print(f"🎯 已聚焦到小程序区域: ({center_x}, {center_y})")
            return True
        except Exception as e:
            print(f"❌ 聚焦失败: {e}")
            return False
    
    def get_mini_program_bounds(self):
        """获取小程序区域边界"""
        if not self.mini_program_bounds:
            return None
        
        return {
            'x': CrawlerConfig.WECHAT_WINDOW_POSITION[0] + self.mini_program_bounds['x'],
            'y': CrawlerConfig.WECHAT_WINDOW_POSITION[1] + self.mini_program_bounds['y'],
            'width': self.mini_program_bounds['width'],
            'height': self.mini_program_bounds['height']
        }
    
    def setup_mini_program_environment(self):
        """设置小程序环境（完整流程）"""
        print("🚀 开始设置小程序环境...")
        
        # 1. 查找并设置微信窗口
        if not self.find_and_setup_wechat_window():
            return False
        
        # 2. 点击小程序入口
        if not self.click_mini_program_entry():
            return False
        
        # 3. 选择第一个小程序
        if not self.select_first_mini_program():
            return False
        
        # 4. 聚焦到小程序区域
        if not self.focus_mini_program_area():
            return False
        
        print("✅ 小程序环境设置完成")
        return True 