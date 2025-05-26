#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫核心类
整合所有组件，提供主要的爬取逻辑
"""

import os
import time
from datetime import datetime
from config import CrawlerConfig
from window_detector import WindowDetector
from screenshot_manager import ScreenshotManager
from interaction_manager import InteractionManager
from analysis_client import AnalysisClient
from data_manager import DataManager

class CrawlerCore:
    """爬虫核心类"""
    
    def __init__(self):
        # 初始化各个组件
        self.window_detector = WindowDetector()
        self.screenshot_manager = ScreenshotManager(self.window_detector)
        self.interaction_manager = InteractionManager(self.window_detector)
        self.analysis_client = AnalysisClient()
        self.data_manager = DataManager()
        
        # 创建输出目录
        CrawlerConfig.create_output_dirs()
        
        print("🚀 微信小程序爬虫核心已初始化")
    
    def start_crawling(self, app_name="微信小程序"):
        """开始爬取流程"""
        print(f"🚀 开始爬取微信小程序: {app_name}")
        
        # 设置应用名称
        self.data_manager.set_app_name(app_name)
        
        # 检查服务器连接
        if not self.analysis_client.check_server_health():
            print("❌ 无法连接到MCP服务器，请确保服务器正在运行")
            return False
        
        # 清理旧截图
        print("🗑️ 清理旧截图文件...")
        CrawlerConfig.clean_screenshots()
        
        # 检测小程序窗口
        mini_program_bounds = self.window_detector.detect_mini_program_window(app_name)
        if not mini_program_bounds:
            print("❌ 无法检测到小程序窗口，请确保小程序已打开并可见")
            return False
        
        print(f"\n📱 小程序窗口检测成功: {mini_program_bounds}")
        print("✅ 准备开始爬取...")
        
        # 开始爬取主页面
        success = self._crawl_main_page()
        
        if success:
            # 完成爬取
            self.data_manager.finalize_crawl_data()
            self.data_manager.save_results()
            
            stats = self.data_manager.get_crawl_stats()
            print(f"\n🎉 爬取完成！")
            print(f"📊 总计爬取 {stats['total_pages']} 个页面")
            print(f"🔘 总计点击 {stats['total_buttons']} 个按钮")
            print(f"⏱️ 总耗时 {stats['duration']} 秒")
            return True
        else:
            print("❌ 爬取失败")
            return False
    
    def _crawl_main_page(self):
        """爬取主页面"""
        # 爬取主页面
        main_page_data = self._crawl_current_page("主页面", is_main_page=True)
        
        if not main_page_data:
            print("❌ 主页面爬取失败")
            return False
        
        self.data_manager.add_page_data(main_page_data)
        
        # 获取主页面的按钮
        buttons = self.interaction_manager.find_clickable_buttons(main_page_data['analysis'])
        print(f"🔍 在主页面发现 {len(buttons)} 个可点击按钮")
        
        # 遍历每个按钮
        for i, button in enumerate(buttons):
            button_id = f"{button['text']}_{button['center_x']}_{button['center_y']}"
            
            if self.data_manager.is_button_visited(button_id):
                print(f"⏭️ 跳过已访问的按钮: {button['text']}")
                continue
            
            self.data_manager.add_visited_button(button_id)
            
            print(f"\n🎯 正在处理按钮 {i+1}/{len(buttons)}: {button['text']}")
            
            # 确保聚焦到小程序区域
            self._focus_mini_program_area()
            
            # 点击按钮
            if self.interaction_manager.click_button(button):
                # 爬取新页面
                page_name = f"{button['text']}_页面"
                page_data = self._crawl_current_page(page_name)
                
                if page_data:
                    page_data['parent_page'] = "主页面"
                    page_data['trigger_button'] = button['text']
                    self.data_manager.add_page_data(page_data)
                    self.data_manager.add_navigation_mapping(button['text'], page_name)
                
                # 返回主页面
                print("🔙 正在返回主页面...")
                if self.interaction_manager.go_back():
                    time.sleep(CrawlerConfig.PAGE_LOAD_DELAY)
                    self._focus_mini_program_area()
                else:
                    print("⚠️ 返回主页面失败，可能需要手动操作")
                    input("请手动返回到主页面，然后按回车继续...")
                    self._focus_mini_program_area()
            
            # 进度提示
            print(f"📊 进度: {i+1}/{len(buttons)} 按钮已处理")
        
        return True
    
    def _crawl_current_page(self, page_name, is_main_page=False):
        """爬取当前页面"""
        print(f"📄 正在爬取小程序页面: {page_name}")
        
        # 确保聚焦到小程序区域
        self._focus_mini_program_area()
        time.sleep(1)
        
        # 截取小程序区域的普通截图
        screenshot_path = self.screenshot_manager.take_mini_program_screenshot(f"{page_name}_normal.png")
        if not screenshot_path:
            print(f"❌ 页面截图失败: {page_name}")
            return None
        
        # 滚动截取小程序的完整页面
        full_screenshot_path, scroll_screenshots = self.screenshot_manager.take_full_page_screenshot()
        if not full_screenshot_path:
            print(f"❌ 完整页面截图失败: {page_name}")
            return None
        
        # 分析完整页面
        analysis_data = self.analysis_client.analyze_screenshot(full_screenshot_path, page_name)
        if not analysis_data:
            print(f"❌ 页面分析失败: {page_name}")
            return None
        
        # 构建页面数据
        page_data = {
            'page_name': page_name,
            'timestamp': datetime.now().isoformat(),
            'is_main_page': is_main_page,
            'screenshots': {
                'normal': os.path.basename(screenshot_path),
                'full_page': os.path.basename(full_screenshot_path),
                'scroll_sequence': [os.path.basename(path) for path in scroll_screenshots]
            },
            'analysis': analysis_data,
            'extracted_features': self.analysis_client.extract_page_features(analysis_data),
            'mini_program_bounds': self.window_detector.get_current_bounds()
        }
        
        print(f"✅ 小程序页面爬取完成: {page_name}")
        return page_data
    
    def _focus_mini_program_area(self):
        """聚焦到小程序区域"""
        center_point = self.window_detector.get_center_point()
        if center_point:
            import pyautogui
            pyautogui.click(center_point[0], center_point[1])
            time.sleep(CrawlerConfig.FOCUS_DELAY)
            print(f"🎯 已聚焦到小程序区域: {center_point}")
        else:
            print("⚠️ 无法获取小程序中心点，跳过聚焦操作") 