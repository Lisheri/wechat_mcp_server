#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边缘分析器
专门负责边缘检测和图像处理算法
"""

import cv2
import numpy as np
from .utils import ScreenshotUtils


class EdgeAnalyzer:
    """边缘分析器"""
    
    def __init__(self):
        pass
    
    def detect_edges_and_contours(self, screenshot_cv):
        """检测边缘和轮廓"""
        height, width = screenshot_cv.shape[:2]
        
        # 转换为HSV色彩空间，更好地检测灰色边框
        hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 检测小程序特有的灰色边框
        gray_frame_mask = cv2.inRange(gray, 80, 200)
        ScreenshotUtils.save_debug_image(gray_frame_mask, "debug_gray_detection.png", "灰色检测结果")
        
        # 使用精确的边缘检测
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        ScreenshotUtils.save_debug_image(edges, "debug_edges_only.png", "边缘检测结果")
        
        # 结合灰色检测和边缘检测
        combined_mask = cv2.bitwise_and(gray_frame_mask, edges)
        
        # 形态学操作，连接边框
        kernel = np.ones((3, 3), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        combined_mask = cv2.dilate(combined_mask, kernel, iterations=2)
        
        ScreenshotUtils.save_debug_image(combined_mask, "debug_combined_detection.png", "组合检测结果")
        
        # 查找轮廓
        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 在原图上绘制检测到的轮廓
        debug_contours = screenshot_cv.copy()
        cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
        ScreenshotUtils.save_debug_image(debug_contours, "debug_contours.png", "轮廓检测结果")
        
        print(f"🔍 检测到 {len(contours)} 个轮廓")
        
        return contours, gray
    
    def calculate_edge_score(self, x, y, w, h, area, aspect_ratio, mean_gray):
        """计算边缘检测评分"""
        score = 0
        
        # 宽度评分（接近414像素）
        width_diff = abs(w - 414)
        if width_diff < 30:
            score += 50
        elif width_diff < 60:
            score += 35
        elif width_diff < 100:
            score += 20
        elif width_diff < 150:
            score += 10
        
        # 长宽比评分
        if 1.2 < aspect_ratio < 2.5:
            score += 25
        elif 0.8 < aspect_ratio < 3.0:
            score += 15
        
        # 灰色特征评分
        if 80 < mean_gray < 180:
            score += 20
        elif 50 < mean_gray < 220:
            score += 10
        
        # 面积评分
        if area > 100000:
            score += 12
        elif area > 60000:
            score += 8
        elif area > 30000:
            score += 4
        
        return score 