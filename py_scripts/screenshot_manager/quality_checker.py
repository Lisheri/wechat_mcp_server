#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量检查器
专门负责截图内容质量检查和评分
"""

import os
import cv2
import numpy as np
from PIL import Image
from .utils import ScreenshotUtils


class QualityChecker:
    """质量检查器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
    
    def calculate_quality_score(self, actual_width, actual_height, target_width):
        """计算质量评分"""
        width_diff = abs(actual_width - target_width)
        aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(actual_width, actual_height)
        
        score = 0
        
        # 宽度评分（50分）
        if width_diff <= 5:
            score += 50
        elif width_diff <= 15:
            score += 45
        elif width_diff <= 30:
            score += 35
        elif width_diff <= 60:
            score += 20
        elif width_diff <= 100:
            score += 10
        
        # 长宽比评分（25分）
        if 1.5 <= aspect_ratio <= 2.2:
            score += 25
        elif 1.2 <= aspect_ratio <= 2.5:
            score += 20
        elif 1.0 <= aspect_ratio <= 3.0:
            score += 10
        
        # 尺寸合理性评分（25分）
        if ScreenshotUtils.is_size_in_range(actual_width, actual_height):
            score += 25
        elif actual_width >= 250 and actual_height >= 300:
            score += 15
        elif actual_width >= 200 and actual_height >= 200:
            score += 10
        
        return min(score, 100)
    
    def validate_screenshot_content(self, screenshot_path):
        """验证截图内容质量"""
        try:
            if not os.path.exists(screenshot_path):
                return False
            
            # 加载图像
            image = cv2.imread(screenshot_path)
            if image is None:
                print(f"❌ 无法加载截图: {screenshot_path}")
                return False
            
            height, width = image.shape[:2]
            
            # 转换为灰度图像
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 检查1: 内容复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # 检查2: 颜色多样性
            color_variance = np.var(image, axis=2)
            avg_variance = np.mean(color_variance)
            
            # 检查3: 亮度分布
            brightness_mean = np.mean(gray)
            brightness_std = np.std(gray)
            
            print(f"📊 内容质量分析:")
            print(f"   边缘密度: {edge_density:.4f}")
            print(f"   颜色方差: {avg_variance:.2f}")
            print(f"   平均亮度: {brightness_mean:.1f}")
            print(f"   亮度标准差: {brightness_std:.1f}")
            
            # 综合判断
            is_valid = (edge_density > 0.01 and 
                       avg_variance > 50 and 
                       50 < brightness_mean < 200 and 
                       brightness_std > 20)
            
            if is_valid:
                print(f"   ✅ 内容质量验证通过")
            else:
                print(f"   ❌ 内容质量验证失败")
            
            return is_valid
            
        except Exception as e:
            print(f"❌ 内容验证失败: {e}")
            return False
    
    def get_screenshot_info(self, screenshot_path):
        """获取截图详细信息"""
        try:
            if not os.path.exists(screenshot_path):
                return None
            
            with Image.open(screenshot_path) as img:
                width, height = img.size
                file_size = os.path.getsize(screenshot_path)
                
            aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(width, height)
            
            return {
                'path': screenshot_path,
                'width': width,
                'height': height,
                'aspect_ratio': aspect_ratio,
                'file_size': file_size,
                'file_size_mb': file_size / (1024 * 1024)
            }
            
        except Exception as e:
            print(f"❌ 获取截图信息失败: {e}")
            return None 