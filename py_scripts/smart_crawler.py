#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爬虫核心类 - 重构版本
整合所有组件，提供主要的爬取逻辑，支持智能按钮识别和分类截图
"""

from crawler_core.main_crawler import MainCrawler


class CrawlerCore:
    """爬虫核心类 - 兼容性包装器"""
    
    def __init__(self):
        """初始化爬虫核心"""
        self.main_crawler = MainCrawler()
        print("🚀 微信小程序爬虫核心已初始化（使用智能模式）")
    
    def start_crawling(self, app_name="微信小程序"):
        """开始爬取流程"""
        return self.main_crawler.start_crawling(app_name)
    
    def get_crawling_progress(self):
        """获取爬取进度"""
        return self.main_crawler.get_crawling_progress()
    
    # 提供对新组件的访问
    @property
    def window_manager(self):
        return self.main_crawler.window_manager
    
    @property
    def screenshot_manager(self):
        return self.main_crawler.screenshot_manager
    
    @property
    def analysis_client(self):
        return self.main_crawler.analysis_client
    
    @property
    def data_manager(self):
        return self.main_crawler.data_manager
    
    @property
    def directory_manager(self):
        return self.main_crawler.directory_manager
    
    @property
    def button_detector(self):
        return self.main_crawler.button_detector
    
    @property
    def button_navigator(self):
        return self.main_crawler.button_navigator 