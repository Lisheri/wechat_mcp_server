#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主爬虫器
负责整体的爬取流程控制和协调各个子模块
"""

import time
from datetime import datetime
from config import CrawlerConfig
from wechat_window_manager import WeChatWindowManager
from screenshot_manager import ScreenshotManager
from analysis_client import AnalysisClient
from data_manager import DataManager
from directory_manager import DirectoryManager
from button_manager import ButtonDetector, ButtonNavigator
from .page_crawler import PageCrawler
from .smart_navigator import SmartNavigator


class MainCrawler:
    """主爬虫器类"""
    
    def __init__(self):
        """初始化主爬虫器"""
        # 基础组件
        self.window_manager = WeChatWindowManager()
        self.analysis_client = AnalysisClient()
        self.data_manager = DataManager()
        self.directory_manager = DirectoryManager()
        
        # 截图管理器需要目录管理器
        self.screenshot_manager = ScreenshotManager(self.window_manager, self.directory_manager)
        
        # 智能导航组件
        self.button_detector = ButtonDetector()
        self.button_navigator = ButtonNavigator(self.window_manager)
        
        # 专用爬虫器
        self.page_crawler = PageCrawler(
            self.window_manager, 
            self.screenshot_manager, 
            self.analysis_client,
            self.directory_manager
        )
        
        self.smart_navigator = SmartNavigator(
            self.button_detector,
            self.button_navigator,
            self.window_manager
        )
        
        # 创建输出目录
        CrawlerConfig.create_output_dirs()
        
        print("🚀 智能微信小程序爬虫已初始化")
    
    def start_crawling(self, app_name="微信小程序"):
        """开始智能爬取流程"""
        print(f"🚀 开始智能爬取微信小程序: {app_name}")
        
        # 设置应用名称
        self.data_manager.set_app_name(app_name)
        
        # 检查服务器连接
        if not self.analysis_client.check_server_health():
            print("❌ 无法连接到MCP服务器，请确保服务器正在运行")
            return False
        
        # 设置小程序环境
        if not self.window_manager.setup_mini_program_environment():
            print("❌ 无法设置小程序环境，请确保微信已打开")
            return False
        
        mini_program_bounds = self.window_manager.get_mini_program_bounds()
        print(f"\n📱 小程序区域设置成功: {mini_program_bounds}")
        
        # 清理上一轮截图
        self.screenshot_manager.start_screenshot_session()
        
        try:
            # 开始智能爬取
            success = self._start_smart_crawling(mini_program_bounds)
            
            if success:
                self._finalize_crawling()
                return True
            else:
                print("❌ 爬取失败")
                return False
                
        except Exception as e:
            print(f"❌ 爬取过程出错: {e}")
            return False
    
    def _start_smart_crawling(self, bounds):
        """开始智能爬取流程"""
        print("🧠 开始智能按钮识别和分类爬取...")
        
        # 检测主页面按钮
        target_buttons = self.smart_navigator.detect_main_page_buttons(bounds)
        
        if not target_buttons:
            print("❌ 未检测到任何目标按钮")
            return False
        
        print(f"🎯 检测到 {len(target_buttons)} 个目标按钮")
        
        # 逐个处理按钮
        for i, button in enumerate(target_buttons):
            print(f"\n{'='*50}")
            print(f"🎯 处理按钮 {i+1}/{len(target_buttons)}: {button['target']}")
            print(f"{'='*50}")
            
            success = self._process_single_button(button, bounds)
            
            if not success:
                print(f"⚠️ 按钮 {button['target']} 处理失败，继续下一个")
                continue
            
            # 进度显示
            progress = (i + 1) / len(target_buttons) * 100
            print(f"📊 整体进度: {progress:.1f}% ({i+1}/{len(target_buttons)})")
        
        print("\n🎉 所有按钮处理完成！")
        return True
    
    def _process_single_button(self, button, bounds):
        """处理单个按钮的完整流程"""
        try:
            print(f"\n🔧 准备处理按钮: {button['target']}")
            
            # 在处理每个按钮前，重新确认环境状态
            self._ensure_environment_ready(bounds)
            
            # 1. 创建按钮专用目录
            button_dir = self.directory_manager.create_button_directory(button['target'])
            if not button_dir:
                return False
            
            # 2. 导航到按钮页面
            print(f"🧭 导航到按钮页面: {button['target']}")
            if not self.smart_navigator.navigate_to_button_page(button, bounds):
                print(f"❌ 导航到按钮页面失败: {button['target']}")
                return False
            
            # 3. 等待页面稳定
            print(f"⏳ 等待页面稳定...")
            time.sleep(2)
            
            # 4. 爬取内页
            print(f"📄 开始爬取内页内容: {button['target']}")
            page_data = self.page_crawler.crawl_inner_page(button['target'])
            if not page_data:
                print(f"❌ 内页爬取失败: {button['target']}")
                # 即使爬取失败，也尝试返回主页
                self.smart_navigator.return_to_main_page(bounds)
                return False
            
            # 5. 返回主页
            print(f"🔙 返回主页...")
            return_success = self.smart_navigator.return_to_main_page(bounds)
            if not return_success:
                print(f"⚠️ 返回主页失败，尝试重新设置环境")
                # 重新设置环境以准备处理下一个按钮
                self.window_manager.setup_mini_program_environment()
                time.sleep(2)
            
            # 6. 记录数据
            self.data_manager.add_page_data(page_data)
            
            print(f"✅ 按钮 {button['target']} 处理完成")
            return True
            
        except Exception as e:
            print(f"❌ 处理按钮 {button['target']} 时出错: {e}")
            # 发生异常时，尝试返回主页
            try:
                self.smart_navigator.return_to_main_page(bounds)
            except:
                pass
            return False
    
    def _ensure_environment_ready(self, bounds):
        """确保环境状态准备就绪"""
        try:
            print(f"🔧 检查并确保环境状态就绪...")
            
            # 检查window_manager状态
            if not hasattr(self.window_manager, '_mini_program_bounds') or not self.window_manager._mini_program_bounds:
                print(f"⚠️ 小程序环境丢失，重新设置...")
                self.window_manager.setup_mini_program_environment()
            
            # 确保聚焦到正确位置
            self.window_manager.focus_mini_program_area()
            
            # 重置截图管理器的检测缓存
            if hasattr(self.screenshot_manager, 'detection_strategy'):
                print(f"🔄 重置检测缓存...")
            
            time.sleep(1)
            print(f"✅ 环境状态检查完成")
            
        except Exception as e:
            print(f"⚠️ 环境检查失败: {e}")
            # 如果检查失败，强制重新设置
            self.window_manager.setup_mini_program_environment()
    
    def _finalize_crawling(self):
        """完成爬取，保存结果"""
        print("\n🏁 正在完成爬取...")
        
        # 保存结果
        self.data_manager.finalize_crawl_data()
        self.data_manager.save_results()
        
        # 清理空目录
        self.directory_manager.cleanup_empty_directories()
        
        # 统计信息
        stats = self.data_manager.get_crawl_stats()
        dir_summary = self.directory_manager.get_directory_summary()
        nav_summary = self.button_navigator.get_navigation_summary()
        
        print(f"\n🎉 爬取完成！")
        print(f"📊 总计爬取 {stats.get('total_pages', 0)} 个页面")
        print(f"📁 创建 {dir_summary['total_directories']} 个分类目录")
        print(f"📸 保存 {dir_summary['total_screenshots']} 张截图")
        print(f"🧭 访问 {nav_summary['total_navigations']} 个页面")
        print(f"⏱️ 总耗时 {stats.get('duration', 0)} 秒")
        
        # 显示目录摘要
        if dir_summary['directories']:
            print(f"\n📁 截图分类目录:")
            for dir_name, count in dir_summary['directories'].items():
                print(f"  📂 {dir_name}: {count} 张截图")
    
    def get_crawling_progress(self):
        """获取爬取进度"""
        nav_summary = self.button_navigator.get_navigation_summary()
        dir_summary = self.directory_manager.get_directory_summary()
        
        return {
            'current_page': nav_summary['current_page'],
            'pages_visited': nav_summary['unique_pages_visited'],
            'total_navigations': nav_summary['total_navigations'],
            'directories_created': dir_summary['total_directories'],
            'screenshots_taken': dir_summary['total_screenshots']
        } 