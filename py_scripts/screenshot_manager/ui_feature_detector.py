#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UI特征检测器
专门负责检测UI元素和界面特征
"""

import cv2
import numpy as np
from .utils import ScreenshotUtils


class UIFeatureDetector:
    """UI特征检测器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
    
    def detect_ui_features(self, screenshot_cv):
        """检测UI特征"""
        height, width = screenshot_cv.shape[:2]
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 检测水平分割线（小程序常见UI元素）
        horizontal_lines = self.detect_horizontal_lines(gray)
        
        if len(horizontal_lines) >= 2:
            # 有足够的水平线，可能是小程序界面
            print(f"   🎯 检测到 {len(horizontal_lines)} 条水平分割线，可能是小程序界面")
            
            # 基于水平线确定内容区域
            top_line = min(horizontal_lines, key=lambda x: x[1])
            bottom_line = max(horizontal_lines, key=lambda x: x[1])
            
            content_bounds = {
                'x': 50,  # 留一些边距
                'y': top_line[1],
                'width': width - 100,
                'height': bottom_line[1] - top_line[1]
            }
            
            if content_bounds['height'] > 300:  # 确保高度合理
                return content_bounds
        
        return None
    
    def detect_horizontal_lines(self, gray):
        """检测水平线"""
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=100, maxLineGap=10)
        
        horizontal_lines = []
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                # 检查是否为水平线（角度接近0度）
                angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
                if angle < 10 or angle > 170:  # 水平线
                    horizontal_lines.append((x1, y1, x2, y2))
        
        return horizontal_lines
    
    def detect_miniprogram_border(self, screenshot_cv):
        """检测小程序边框"""
        print(f"   🔍 检测小程序边框...")
        
        height, width = screenshot_cv.shape[:2]
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 使用更精确的边缘检测
        edges = cv2.Canny(gray, 30, 100)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 寻找最大的矩形轮廓
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > width * height * 0.3:  # 至少占30%的面积
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(w, h)
                
                if 1.0 < aspect_ratio < 3.0 and w > 300 and h > 400:
                    print(f"   ✅ 发现可能的小程序边框: ({x},{y},{w},{h})")
                    return {'x': x, 'y': y, 'width': w, 'height': h}
        
        return None 