#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容分析器
专门负责内容密度分析和图像处理
"""

import cv2
import numpy as np
from .utils import ScreenshotUtils


class ContentAnalyzer:
    """内容分析器"""
    
    def __init__(self):
        pass
    
    def analyze_content_density(self, screenshot_cv, wechat_bounds):
        """分析内容密度"""
        height, width = screenshot_cv.shape[:2]
        
        # 转换为HSV色彩空间
        hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 检测有意义的内容区域（排除纯黑、纯白、纯灰等边框色彩）
        lower_content = np.array([0, 10, 50])
        upper_content = np.array([180, 255, 240])
        content_mask = cv2.inRange(hsv, lower_content, upper_content)
        
        # 使用边缘检测找到文字和UI元素
        edges = cv2.Canny(gray, 30, 100)
        
        # 膨胀边缘以连接相邻的文字和元素
        kernel = np.ones((3, 3), np.uint8)
        edges_dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # 合并内容掩码和边缘检测结果
        combined_mask = cv2.bitwise_or(content_mask, edges_dilated)
        
        # 形态学操作，连接相邻的内容区域
        kernel = np.ones((5, 5), np.uint8)
        combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
        
        # 保存内容掩码调试图像
        ScreenshotUtils.save_debug_image(combined_mask, "debug_content_mask.png", "内容掩码图像")
        
        return combined_mask
    
    def calculate_column_density(self, combined_mask):
        """计算每列的内容密度"""
        height, width = combined_mask.shape[:2]
        column_content_density = []
        
        for col in range(width):
            column_mask = combined_mask[:, col]
            content_pixels = np.sum(column_mask > 0)
            total_pixels = len(column_mask)
            density = content_pixels / total_pixels if total_pixels > 0 else 0
            column_content_density.append(density)
        
        return column_content_density
    
    def find_high_density_columns(self, column_content_density, threshold=0.20):
        """查找高密度列"""
        return [i for i, density in enumerate(column_content_density) if density > threshold]
    
    def group_continuous_regions(self, high_density_columns, min_width=250, max_gap=5):
        """将连续的高密度列分组为区域"""
        if not high_density_columns:
            return []
        
        content_regions = []
        start = high_density_columns[0]
        end = start
        
        for i in range(1, len(high_density_columns)):
            if high_density_columns[i] - high_density_columns[i-1] <= max_gap:
                end = high_density_columns[i]
            else:
                if end - start > min_width:
                    content_regions.append((start, end))
                start = high_density_columns[i]
                end = start
        
        # 添加最后一个区域
        if end - start > min_width:
            content_regions.append((start, end))
        
        return content_regions
    
    def calculate_row_density(self, combined_mask, left_boundary, right_boundary):
        """计算指定列范围内每行的内容密度"""
        height = combined_mask.shape[0]
        row_content_density = []
        
        for row in range(height):
            row_mask = combined_mask[row, left_boundary:right_boundary]
            content_pixels = np.sum(row_mask > 0)
            total_pixels = len(row_mask)
            density = content_pixels / total_pixels if total_pixels > 0 else 0
            row_content_density.append(density)
        
        return row_content_density
    
    def find_vertical_boundaries(self, row_content_density, threshold=0.10):
        """根据行密度查找垂直边界"""
        high_density_rows = [i for i, density in enumerate(row_content_density) if density > threshold]
        
        if high_density_rows:
            top_boundary = min(high_density_rows)
            bottom_boundary = max(high_density_rows)
            return top_boundary, bottom_boundary
        
        return None, None 