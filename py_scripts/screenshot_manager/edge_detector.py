#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
边缘检测器
基于边缘检测技术识别小程序的灰色边框
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageGrab
from config import CrawlerConfig
from .utils import ScreenshotUtils
from .edge_analysis import EdgeAnalyzer
from .contour_processor import ContourProcessor


class EdgeDetector:
    """边缘检测器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.utils = ScreenshotUtils()
        self.analyzer = EdgeAnalyzer()
        self.processor = ContourProcessor()
    
    def detect_miniprogram_edges(self):
        """通过边缘检测识别小程序的灰色边框"""
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
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            height, width = screenshot_cv.shape[:2]
            
            # 保存原始图像
            ScreenshotUtils.save_debug_image(screenshot_cv, "debug_edge_detection.png", "边缘检测调试图像")
            
            # 检测小程序边框
            candidates = self._detect_edges_and_contours(screenshot_cv)
            
            if candidates:
                # 选择最佳候选区域
                best_candidate = self.processor.select_best_candidate(candidates)
                
                if best_candidate and best_candidate['score'] > 30:
                    x, y, w, h = best_candidate['bounds']
                    
                    # 转换为全局坐标
                    actual_bounds = {
                        'x': wechat_bounds['x'] + x,
                        'y': wechat_bounds['y'] + y,
                        'width': w,
                        'height': h
                    }
                    
                    print(f"🎯 边缘检测到小程序区域: {actual_bounds}")
                    print(f"   评分: {best_candidate['score']}")
                    print(f"   宽度与目标414像素的差距: {abs(w - 414)} 像素")
                    
                    return actual_bounds
                else:
                    print(f"⚠️ 边缘检测候选区域评分过低")
            else:
                print("⚠️ 边缘检测未找到合适的小程序区域")
            
        except Exception as e:
            print(f"⚠️ 边缘检测失败: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def _detect_edges_and_contours(self, screenshot_cv):
        """检测边缘和轮廓"""
        height, width = screenshot_cv.shape[:2]
        
        # 使用边缘分析器进行检测
        contours, gray = self.analyzer.detect_edges_and_contours(screenshot_cv)
        
        # 使用轮廓处理器分析结果
        return self.processor.analyze_contours(contours, gray, width, height) 