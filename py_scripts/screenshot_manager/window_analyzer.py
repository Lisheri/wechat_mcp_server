#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口内容分析器
专门负责分析窗口内容，验证是否为小程序内容
"""

import cv2
import numpy as np
from .utils import ScreenshotUtils
from .ui_feature_detector import UIFeatureDetector


class WindowContentAnalyzer:
    """窗口内容分析器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
        self.ui_detector = UIFeatureDetector()
    
    def analyze_window_for_miniprogram(self, screenshot_cv, window_title):
        """分析窗口是否包含小程序内容"""
        height, width = screenshot_cv.shape[:2]
        print(f"   📐 窗口内容尺寸: {width}x{height}")
        
        # 特殊情况：如果窗口尺寸本身就符合小程序特征，直接使用整个窗口
        aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(width, height)
        
        if (350 <= width <= 500 and 500 <= height <= 900 and 1.2 <= aspect_ratio <= 2.5):
            print(f"   🎯 窗口尺寸符合小程序特征，直接使用整个窗口")
            print(f"   📏 宽度: {width}, 高度: {height}, 长宽比: {aspect_ratio:.2f}")
            
            # 验证这确实是小程序内容
            if self.verify_miniprogram_content(screenshot_cv):
                return {
                    'x': 0,
                    'y': 0,
                    'width': width,
                    'height': height
                }
            else:
                print(f"   ⚠️ 窗口尺寸符合但内容验证失败")
        
        # 如果不符合直接使用条件，进行详细分析
        return self.detailed_content_analysis(screenshot_cv, window_title)
    
    def verify_miniprogram_content(self, screenshot_cv):
        """验证是否为小程序内容"""
        try:
            height, width = screenshot_cv.shape[:2]
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # 检查1: 内容复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # 检查2: 颜色多样性
            color_variance = np.var(screenshot_cv, axis=2)
            avg_variance = np.mean(color_variance)
            
            # 检查3: 文字区域
            text_regions = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
            text_density = np.sum(text_regions > 0) / (width * height)
            
            print(f"   🔍 内容验证: 边缘密度{edge_density:.3f}, 颜色方差{avg_variance:.1f}, 文字密度{text_density:.3f}")
            
            # 综合判断
            if edge_density > 0.02 and avg_variance > 100 and text_density > 0.01:
                print(f"   ✅ 内容验证通过")
                return True
            else:
                print(f"   ❌ 内容验证失败")
                return False
                
        except Exception as e:
            print(f"   ⚠️ 内容验证异常: {e}")
            return False
    
    def detailed_content_analysis(self, screenshot_cv, window_title):
        """详细的窗口内容分析"""
        print(f"   🔍 进行详细窗口内容分析...")
        
        # 检测UI特征
        ui_bounds = self.ui_detector.detect_ui_features(screenshot_cv)
        if ui_bounds:
            return ui_bounds
        
        # 检测边框
        border_bounds = self.ui_detector.detect_miniprogram_border(screenshot_cv)
        if border_bounds:
            return border_bounds
        
        return None 