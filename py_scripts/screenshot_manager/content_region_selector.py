#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容区域选择器
专门负责选择最佳的内容区域
"""


class ContentRegionSelector:
    """内容区域选择器"""
    
    def __init__(self):
        pass
    
    def select_best_content_region(self, content_regions, combined_mask, height):
        """选择最佳内容区域"""
        best_region = None
        best_score = 0
        
        for start_col, end_col in content_regions:
            region_width = end_col - start_col
            width_diff = abs(region_width - 414)
            
            # 计算评分
            score = self._calculate_region_score(region_width, width_diff, start_col, end_col, combined_mask)
            
            print(f"   内容区域: 列{start_col}-{end_col}, 宽度{region_width}, 评分{score}")
            
            if score > best_score:
                best_score = score
                best_region = (start_col, end_col)
        
        if best_region and best_score > 25:
            return best_region
        
        return None
    
    def _calculate_region_score(self, region_width, width_diff, start_col, end_col, combined_mask):
        """计算区域评分"""
        score = 0
        
        # 宽度差距评分
        if width_diff < 10:
            score += 80
        elif width_diff < 20:
            score += 60
        elif width_diff < 40:
            score += 40
        elif width_diff < 80:
            score += 20
        elif width_diff < 120:
            score += 10
        
        # 位置评分（中心偏右的区域得分更高）
        center_x = (start_col + end_col) // 2
        if center_x > combined_mask.shape[1] * 0.3:
            score += 15
        
        # 宽度合理性评分
        if 350 < region_width < 450:
            score += 25
        elif 300 < region_width < 480:
            score += 15
        
        return score
    
    def validate_content_region(self, left_boundary, right_boundary, top_boundary, bottom_boundary, wechat_bounds):
        """验证内容区域是否有效"""
        if top_boundary is None or bottom_boundary is None:
            return None
        
        content_width = right_boundary - left_boundary
        content_height = bottom_boundary - top_boundary
        
        if content_height > 400:
            actual_bounds = {
                'x': wechat_bounds['x'] + left_boundary,
                'y': wechat_bounds['y'] + top_boundary,
                'width': content_width,
                'height': content_height
            }
            print(f"   宽度与目标414像素的差距: {abs(content_width - 414)} 像素")
            return actual_bounds
        
        return None 