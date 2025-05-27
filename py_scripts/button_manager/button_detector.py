#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮检测器
整合OCR识别和按钮匹配功能，检测小程序中的目标按钮
"""

import os
import time
from PIL import ImageGrab
from ocr_manager import TextDetector, ButtonMatcher


class ButtonDetector:
    """按钮检测器类"""
    
    def __init__(self):
        """初始化按钮检测器"""
        self.text_detector = TextDetector()
        self.button_matcher = ButtonMatcher()
        self.last_detection_result = None
    
    def detect_buttons_in_bounds(self, bounds):
        """在指定区域检测目标按钮"""
        print(f"🔍 开始在区域中检测按钮...")
        
        try:
            # 截取指定区域
            screenshot = ImageGrab.grab(bbox=(
                bounds['x'], bounds['y'],
                bounds['x'] + bounds['width'],
                bounds['y'] + bounds['height']
            ))
            
            # 保存临时截图用于OCR
            temp_path = "/tmp/button_detection.png"
            screenshot.save(temp_path)
            
            # 进行OCR识别
            text_items = self.text_detector.detect_text_from_image(temp_path)
            
            if not text_items:
                print("❌ 未检测到任何文字")
                return []
            
            print(f"📝 检测到 {len(text_items)} 个文字区域")
            
            # 匹配目标按钮
            matched_buttons = self.button_matcher.find_target_buttons(text_items)
            
            # 过滤有效按钮
            valid_buttons = self.button_matcher.filter_valid_buttons(matched_buttons, bounds)
            
            # 保存检测结果
            self.last_detection_result = {
                'bounds': bounds,
                'text_items': text_items,
                'matched_buttons': matched_buttons,
                'valid_buttons': valid_buttons,
                'timestamp': time.time()
            }
            
            # 清理临时文件
            try:
                os.remove(temp_path)
            except:
                pass
            
            return valid_buttons
            
        except Exception as e:
            print(f"❌ 按钮检测失败: {e}")
            return []
    
    def get_button_click_position(self, button, bounds):
        """获取按钮的绝对点击位置"""
        return self.button_matcher.get_click_position(button, bounds)
    
    def check_is_main_page(self, bounds=None):
        """检查当前是否在主页面
        
        判断逻辑：通过多点取色检测左上角返回按钮区域
        如果检测到返回按钮（浅色箭头图标），则为内页
        如果没有检测到返回按钮，则为主页
        """
        if not bounds:
            if hasattr(self.window_manager, '_mini_program_bounds'):
                bounds = self.window_manager._mini_program_bounds
            else:
                print("⚠️ 无法获取小程序边界")
                return True  # 默认认为是主页
        
        print("🔍 开始检测页面类型...")
        
        # 使用多点取色检测左上角返回按钮
        has_return_button = self._detect_return_button_by_color_sampling(bounds)
        
        if has_return_button:
            print("🏠 检测为内页面（发现返回按钮）")
            return False  # 有返回按钮，是内页
        else:
            print("🏠 检测为主页面（无返回按钮）")
            return True  # 无返回按钮，是主页
    
    def _detect_return_button_by_color_sampling(self, bounds):
        """通过多点取色检测返回按钮"""
        try:
            from PIL import ImageGrab
            import numpy as np
            
            # 计算左上角返回按钮区域
            if isinstance(bounds, dict):
                x, y, width, height = bounds['x'], bounds['y'], bounds['width'], bounds['height']
            else:
                x, y, width, height = bounds
            
            # 调整返回按钮区域（顶部20px安全区域）
            # 从图片看，返回按钮在左上角，黑色箭头在白色背景上
            button_region = {
                'x': x + 15,  # 左边偏移15像素
                'y': y + 20,  # 顶部偏移20像素（顶部20px安全区域）
                'width': 40,  # 按钮区域宽度（圆形按钮大约40像素）
                'height': 40  # 按钮区域高度
            }
            
            # 截取返回按钮区域
            screenshot = ImageGrab.grab(bbox=(
                button_region['x'], button_region['y'],
                button_region['x'] + button_region['width'],
                button_region['y'] + button_region['height']
            ))
            
            # 保存调试图片
            debug_path = "/tmp/return_button_debug.png"
            screenshot.save(debug_path)
            print(f"🔍 已保存返回按钮区域调试图片: {debug_path}")
            
            # 转换为numpy数组进行分析
            pixel_array = np.array(screenshot)
            height_px, width_px = pixel_array.shape[:2]
            
            # 定义多个采样点来检测返回按钮
            sample_points = self._get_return_button_sample_points(width_px, height_px)
            
            # 检测返回按钮特征
            return self._analyze_return_button_colors(pixel_array, sample_points)
            
        except Exception as e:
            print(f"⚠️ 返回按钮检测失败: {e}")
            return False
    
    def _get_return_button_sample_points(self, width, height):
        """获取返回按钮的采样点位置"""
        # 返回按钮是一个圆形区域内的黑色左箭头（黑色箭头，白色背景）
        center_x = width // 2
        center_y = height // 2
        
        sample_points = [
            # 中心点（箭头中心）
            (center_x, center_y),
            # 箭头左侧尖端（黑色箭头的关键特征点）
            (center_x - 8, center_y),
            # 箭头右侧上下两点
            (center_x + 4, center_y - 4),
            (center_x + 4, center_y + 4),
            # 箭头主体的几个点
            (center_x - 4, center_y - 2),
            (center_x - 4, center_y + 2),
            # 圆形按钮边缘的背景点（白色背景）
            (2, 2),                    # 左上角
            (width - 2, 2),           # 右上角  
            (2, height - 2),          # 左下角
            (width - 2, height - 2),  # 右下角
            # 圆形边缘的中点
            (center_x, 2),            # 顶部中点
            (center_x, height - 2),   # 底部中点
            (2, center_y),            # 左侧中点
            (width - 2, center_y),    # 右侧中点
        ]
        
        # 确保采样点在有效范围内
        valid_points = []
        for x, y in sample_points:
            if 0 <= x < width and 0 <= y < height:
                valid_points.append((x, y))
        
        return valid_points
    
    def _analyze_return_button_colors(self, pixel_array, sample_points):
        """分析采样点颜色来判断是否有返回按钮（黑色箭头，白色背景）"""
        try:
            if len(sample_points) < 6:
                print("   采样点不足，无法分析")
                return False
            
            # 获取所有采样点的颜色
            colors = []
            for x, y in sample_points:
                r, g, b = pixel_array[y, x][:3]  # 注意numpy数组的坐标顺序
                brightness = (r + g + b) / 3
                colors.append((r, g, b, brightness, x, y))
            
            print(f"   采样了 {len(colors)} 个点的颜色")
            
            # 分析颜色模式
            # 返回按钮的特征：
            # 1. 中心区域有黑色箭头（亮度<80）
            # 2. 边缘有白色背景（亮度>200）
            # 3. 明显的黑白对比
            
            dark_colors = []        # 深色点（黑色箭头）
            light_colors = []       # 亮色点（白色背景）
            medium_colors = []      # 中等亮度点
            
            for r, g, b, brightness, x, y in colors:
                if brightness < 80:      # 深色（黑色箭头）
                    dark_colors.append((r, g, b, brightness, x, y))
                elif brightness > 200:   # 亮色（白色背景）
                    light_colors.append((r, g, b, brightness, x, y))
                else:                    # 中等亮度
                    medium_colors.append((r, g, b, brightness, x, y))
            
            print(f"   深色点: {len(dark_colors)}, 亮色点: {len(light_colors)}, 中等点: {len(medium_colors)}")
            
            # 检查中心区域的箭头特征
            # 前6个采样点是箭头的关键部位，应该是深色（黑色箭头）
            arrow_points = sample_points[:6]
            arrow_dark_count = 0
            
            for x, y in arrow_points:
                if y < len(pixel_array) and x < len(pixel_array[0]):
                    r, g, b = pixel_array[y, x][:3]
                    brightness = (r + g + b) / 3
                    if brightness < 120:  # 箭头应该是深色（黑色）
                        arrow_dark_count += 1
            
            print(f"   箭头区域深色点: {arrow_dark_count}/{len(arrow_points)}")
            
            # 判断是否有返回按钮的特征
            # 条件1: 有足够的深色点（黑色箭头）
            has_dark_arrow = len(dark_colors) >= 2
            
            # 条件2: 箭头区域有足够的深色点
            has_arrow_shape = arrow_dark_count >= 3
            
            # 条件3: 有明显的黑白对比
            has_contrast = len(light_colors) >= 3 and len(dark_colors) >= 2
            
            print(f"   黑色箭头: {has_dark_arrow}, 箭头形状: {has_arrow_shape}, 黑白对比: {has_contrast}")
            
            # 如果满足任意两个条件，认为检测到返回按钮
            conditions_met = sum([has_dark_arrow, has_arrow_shape, has_contrast])
            
            if conditions_met >= 2:
                print("   ✅ 检测到返回按钮特征（黑色箭头图标）")
                return True
            else:
                print("   ❌ 未检测到返回按钮特征")
                return False
            
        except Exception as e:
            print(f"⚠️ 颜色分析失败: {e}")
            return False
    
    def get_unmatched_buttons(self):
        """获取未匹配到的按钮列表"""
        if not self.last_detection_result:
            return self.button_matcher.target_buttons
        
        matched_buttons = self.last_detection_result.get('valid_buttons', [])
        return self.button_matcher.get_unmatched_buttons(matched_buttons)
    
    def save_detection_debug_info(self, filepath="/tmp/button_detection_debug.txt"):
        """保存按钮检测的调试信息"""
        if not self.last_detection_result:
            print("⚠️ 没有检测结果可保存")
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write("按钮检测调试信息\n")
                f.write("=" * 50 + "\n\n")
                
                result = self.last_detection_result
                
                f.write(f"检测时间: {time.ctime(result['timestamp'])}\n")
                f.write(f"检测区域: {result['bounds']}\n\n")
                
                f.write(f"检测到的文字 ({len(result['text_items'])}):\n")
                for i, item in enumerate(result['text_items']):
                    f.write(f"  {i+1}. '{item['text']}' 位置:{item['center']} 置信度:{item['confidence']:.2f}\n")
                
                f.write(f"\n匹配的按钮 ({len(result['matched_buttons'])}):\n")
                for i, btn in enumerate(result['matched_buttons']):
                    f.write(f"  {i+1}. 目标:'{btn['target']}' 匹配:'{btn['matched_text']}' 相似度:{btn['similarity']:.2f}\n")
                
                f.write(f"\n有效按钮 ({len(result['valid_buttons'])}):\n")
                for i, btn in enumerate(result['valid_buttons']):
                    f.write(f"  {i+1}. {btn['target']} -> {btn['center']}\n")
            
            print(f"🐛 调试信息已保存: {filepath}")
            
        except Exception as e:
            print(f"❌ 保存调试信息失败: {e}")
    
    def reset_detection_cache(self):
        """重置检测缓存"""
        self.last_detection_result = None
        print("🔄 已重置按钮检测缓存") 