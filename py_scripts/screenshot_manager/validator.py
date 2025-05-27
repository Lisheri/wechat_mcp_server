#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图验证器
负责验证截图质量、尺寸和内容正确性
"""

import os
from PIL import Image
from .utils import ScreenshotUtils
from .quality_checker import QualityChecker


class ScreenshotValidator:
    """截图验证器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
        self.quality_checker = QualityChecker()
    
    def compare_screenshot_with_target(self, screenshot_path, target_width=414):
        """将截图尺寸与目标进行比较"""
        try:
            if not os.path.exists(screenshot_path):
                print(f"⚠️ 截图文件不存在: {screenshot_path}")
                return False
            
            # 打开图像并获取尺寸
            with Image.open(screenshot_path) as img:
                actual_width, actual_height = img.size
            
            width_diff = abs(actual_width - target_width)
            aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(actual_width, actual_height)
            
            print(f"\n📐 截图尺寸验证结果:")
            print(f"   实际尺寸: {actual_width}x{actual_height}")
            print(f"   目标宽度: {target_width}像素")
            print(f"   宽度差距: {width_diff}像素")
            print(f"   长宽比: {aspect_ratio:.2f}")
            
            # 质量评分
            score = self.quality_checker.calculate_quality_score(actual_width, actual_height, target_width)
            print(f"   质量评分: {score}/100")
            
            # 判断截图质量
            if width_diff <= 5:
                print(f"   ✅ 截图质量: 完美匹配！")
                return True
            elif width_diff <= 15:
                print(f"   ✅ 截图质量: 优秀")
                return True
            elif width_diff <= 30:
                print(f"   ⚠️ 截图质量: 良好，但有轻微偏差")
                return True
            elif width_diff <= 60:
                print(f"   ⚠️ 截图质量: 可接受，但偏差较大")
                return False
            else:
                print(f"   ❌ 截图质量: 不符合要求，偏差过大")
                return False
                
        except Exception as e:
            print(f"❌ 截图比较失败: {e}")
            return False
    
    def validate_screenshot_content(self, screenshot_path):
        """验证截图内容质量"""
        return self.quality_checker.validate_screenshot_content(screenshot_path)
    
    def validate_miniprogram_bounds(self, bounds):
        """验证小程序边界的合理性"""
        if not bounds:
            return False
        
        width = bounds['width']
        height = bounds['height']
        aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(width, height)
        
        print(f"📏 边界验证: {ScreenshotUtils.format_bounds_info(bounds)}")
        print(f"   长宽比: {aspect_ratio:.2f}")
        
        # 检查尺寸合理性
        if width < 250 or height < 300:
            print(f"   ❌ 尺寸太小")
            return False
        
        if width > 600 or height > 1000:
            print(f"   ❌ 尺寸过大")
            return False
        
        # 检查长宽比
        if aspect_ratio < 0.8 or aspect_ratio > 3.0:
            print(f"   ❌ 长宽比不合理")
            return False
        
        # 检查位置合理性
        if bounds['x'] < 0 or bounds['y'] < 0:
            print(f"   ❌ 位置坐标为负")
            return False
        
        print(f"   ✅ 边界验证通过")
        return True
    
    def get_screenshot_info(self, screenshot_path):
        """获取截图详细信息"""
        return self.quality_checker.get_screenshot_info(screenshot_path) 