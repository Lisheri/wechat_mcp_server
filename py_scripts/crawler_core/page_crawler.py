#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页面爬虫器
专门负责内页的滚动截图和数据收集
"""

import os
import time
from datetime import datetime


class PageCrawler:
    """页面爬虫器类"""
    
    def __init__(self, window_manager, screenshot_manager, analysis_client, directory_manager):
        """初始化页面爬虫器"""
        self.window_manager = window_manager
        self.screenshot_manager = screenshot_manager
        self.analysis_client = analysis_client
        self.directory_manager = directory_manager
    
    def crawl_inner_page(self, page_name):
        """爬取内页面（滚动截图）"""
        print(f"📄 开始爬取内页: {page_name}")
        
        # 确保window_manager环境已设置
        if not hasattr(self.window_manager, '_mini_program_bounds') or not self.window_manager._mini_program_bounds:
            print("⚠️ 小程序区域未设置，先设置环境")
            if not self.window_manager.setup_mini_program_environment():
                print("❌ 无法设置小程序环境")
                return None
        
        # 获取当前小程序边界信息
        current_bounds = self.window_manager.get_mini_program_bounds()
        print(f"📐 当前小程序区域: {current_bounds}")
        
        # 确保聚焦到小程序区域
        print(f"🎯 聚焦到小程序区域...")
        self.window_manager.focus_mini_program_area()
        time.sleep(1)
        
        try:
            # 开始滚动截图
            print(f"📸 开始执行滚动截图...")
            scroll_screenshots = self.screenshot_manager.take_scrolling_screenshot(page_name)
            
            if not scroll_screenshots:
                print(f"❌ 滚动截图失败: {page_name}")
                print(f"💡 尝试拍摄单张截图作为备用...")
                # 作为备用，尝试拍摄单张截图
                single_screenshot = self.screenshot_manager.take_miniprogram_screenshot(f"{page_name}_single.png")
                if single_screenshot:
                    scroll_screenshots = [single_screenshot]
                    print(f"✅ 备用单张截图成功")
                else:
                    print(f"❌ 备用截图也失败")
                    return None
            
            print(f"📸 滚动截图完成: {len(scroll_screenshots)} 张图片")
            
            # 分析第一张截图作为主要分析对象
            main_screenshot = scroll_screenshots[0]
            print(f"🔍 开始分析主截图: {main_screenshot}")
            
            analysis_data = self.analysis_client.analyze_screenshot(main_screenshot, page_name)
            
            if not analysis_data:
                print(f"❌ 页面分析失败: {page_name}")
                analysis_data = {}
            
            # 构建页面数据
            page_data = {
                'page_name': page_name,
                'timestamp': datetime.now().isoformat(),
                'is_main_page': False,
                'is_inner_page': True,
                'screenshots': {
                    'scroll_sequence': [os.path.basename(path) for path in scroll_screenshots],
                    'main_screenshot': os.path.basename(main_screenshot),
                    'total_screenshots': len(scroll_screenshots)
                },
                'analysis': analysis_data,
                'extracted_features': self.analysis_client.extract_page_features(analysis_data) if analysis_data else {},
                'mini_program_bounds': current_bounds,
                'screenshot_directory': self.directory_manager.current_button_dir
            }
            
            print(f"✅ 内页爬取完成: {page_name}")
            return page_data
            
        except Exception as e:
            print(f"❌ 内页爬取失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_page_screenshot_count(self, page_name):
        """获取指定页面的截图数量"""
        return self.directory_manager.get_button_screenshot_count(page_name)
    
    def validate_page_screenshots(self, screenshots):
        """验证页面截图的质量"""
        if not screenshots:
            return False, "无截图文件"
        
        valid_count = 0
        total_count = len(screenshots)
        
        for screenshot_path in screenshots:
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 1024:  # 至少1KB
                valid_count += 1
        
        success_rate = valid_count / total_count
        
        if success_rate >= 0.8:  # 80%以上成功率认为合格
            return True, f"截图质量良好 ({valid_count}/{total_count})"
        else:
            return False, f"截图质量不佳 ({valid_count}/{total_count})" 