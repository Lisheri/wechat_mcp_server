#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容检测器
基于内容密度分析检测小程序区域
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageGrab
from config import CrawlerConfig
from .utils import ScreenshotUtils
from .content_analysis import ContentAnalyzer
from .content_region_selector import ContentRegionSelector


class ContentDetector:
    """内容检测器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.utils = ScreenshotUtils()
        self.analyzer = ContentAnalyzer()
        self.selector = ContentRegionSelector()
    
    def detect_miniprogram_content(self):
        """基于内容密度分析检测小程序边界"""
        if not self.window_manager.wechat_window_bounds:
            return None
        
        try:
            # 截取整个微信窗口
            wechat_bounds = self.window_manager.wechat_window_bounds
            full_screenshot = ImageGrab.grab(bbox=(
                wechat_bounds['x'],
                wechat_bounds['y'],
                wechat_bounds['x'] + wechat_bounds['width'],
                wechat_bounds['y'] + wechat_bounds['height']
            ))
            
            # 转换为OpenCV格式进行分析
            screenshot_cv = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            height, width = screenshot_cv.shape[:2]
            
            # 保存调试图像
            ScreenshotUtils.save_debug_image(screenshot_cv, "debug_content_detection.png", "内容检测调试图像")
            
            # 进行内容密度分析
            bounds = self._analyze_content_density(screenshot_cv, wechat_bounds)
            
            if bounds:
                print(f"🎯 基于内容密度检测到小程序区域: {bounds}")
                return bounds
            else:
                print("⚠️ 内容密度分析未找到合适的小程序区域")
            
        except Exception as e:
            print(f"⚠️ 内容密度检测失败: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _analyze_content_density(self, screenshot_cv, wechat_bounds):
        """分析内容密度"""
        height, width = screenshot_cv.shape[:2]
        
        # 使用内容分析器进行密度分析
        combined_mask = self.analyzer.analyze_content_density(screenshot_cv, wechat_bounds)
        
        # 计算列密度
        column_content_density = self.analyzer.calculate_column_density(combined_mask)
        
        # 查找高密度列
        high_density_columns = self.analyzer.find_high_density_columns(column_content_density)
        
        if high_density_columns:
            # 分组连续区域
            content_regions = self.analyzer.group_continuous_regions(high_density_columns)
            
            print(f"🔍 检测到 {len(content_regions)} 个高密度内容区域: {content_regions}")
            
            # 选择最佳区域
            best_region = self.selector.select_best_content_region(content_regions, combined_mask, height)
            
            if best_region:
                left_boundary, right_boundary = best_region
                
                # 计算行密度并查找垂直边界
                row_content_density = self.analyzer.calculate_row_density(
                    combined_mask, left_boundary, right_boundary
                )
                top_boundary, bottom_boundary = self.analyzer.find_vertical_boundaries(row_content_density)
                
                # 验证并返回区域
                return self.selector.validate_content_region(
                    left_boundary, right_boundary, top_boundary, bottom_boundary, wechat_bounds
                )
        
        return None 