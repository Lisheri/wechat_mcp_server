#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
轮廓处理器
专门负责分析轮廓并选择最佳候选区域
"""

import cv2
import numpy as np
from .utils import ScreenshotUtils


class ContourProcessor:
    """轮廓处理器"""
    
    def __init__(self):
        self.utils = ScreenshotUtils()
    
    def analyze_contours(self, contours, gray, width, height):
        """分析轮廓，寻找小程序边框"""
        candidates = []
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 20000:
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            
            print(f"🔍 轮廓 {i}: 位置({x},{y}) 尺寸({w}x{h}) 面积({area})")
            
            # 检查区域内的颜色特征
            roi = gray[y:y+h, x:x+w]
            mean_gray = np.mean(roi)
            
            print(f"   颜色特征: 平均灰度{mean_gray:.1f}")
            
            # 检查是否符合小程序特征
            if w > 200 and h > 300:
                aspect_ratio = ScreenshotUtils.calculate_aspect_ratio(w, h)
                
                if (aspect_ratio > 0.8 and 
                    w < width * 0.95 and h < height * 0.95 and
                    50 < mean_gray < 250):
                    
                    score = self._calculate_contour_score(x, y, w, h, area, aspect_ratio, mean_gray)
                    
                    candidates.append({
                        'bounds': (x, y, w, h),
                        'contour': contour,
                        'score': score,
                        'area': area,
                        'aspect_ratio': aspect_ratio,
                        'mean_gray': mean_gray
                    })
                    
                    print(f"✅ 边缘检测候选区域 {i}: ({x},{y},{w},{h})")
                    print(f"   面积:{area}, 长宽比:{aspect_ratio:.2f}, 平均灰度:{mean_gray:.1f}")
                    print(f"   评分:{score}")
                else:
                    print(f"   ❌ 不符合小程序特征")
            else:
                print(f"   ❌ 尺寸太小: {w}x{h}")
        
        return candidates
    
    def _calculate_contour_score(self, x, y, w, h, area, aspect_ratio, mean_gray):
        """计算轮廓评分"""
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
    
    def select_best_candidate(self, candidates):
        """选择最佳候选区域"""
        if not candidates:
            return None
        
        # 按评分排序
        candidates.sort(key=lambda x: x['score'], reverse=True)
        best_candidate = candidates[0]
        
        print(f"\n📊 找到 {len(candidates)} 个候选区域，最佳评分: {best_candidate['score']}")
        
        # 显示前3个候选区域的详细信息
        for i, candidate in enumerate(candidates[:3]):
            x, y, w, h = candidate['bounds']
            print(f"   候选{i+1}: ({x},{y},{w},{h}) 评分:{candidate['score']} 灰度:{candidate['mean_gray']:.1f}")
        
        return best_candidate 