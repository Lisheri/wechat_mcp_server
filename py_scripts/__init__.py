#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序爬虫包
包含所有爬虫相关的模块和功能
"""

from .config import CrawlerConfig
from .wechat_window_manager import WeChatWindowManager
from .screenshot_manager import ScreenshotManager
from .interaction_manager import InteractionManager
from .analysis_client import AnalysisClient
from .data_manager import DataManager
from .crawler_core import CrawlerCore

__version__ = "2.1.0"
__author__ = "WeChat Mini Program Crawler Team"

__all__ = [
    'CrawlerConfig',
    'WeChatWindowManager',
    'ScreenshotManager', 
    'InteractionManager',
    'AnalysisClient',
    'DataManager',
    'CrawlerCore'
] 