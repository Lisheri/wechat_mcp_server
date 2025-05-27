#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检测策略模块
负责协调多种检测方法，实现智能检测策略
"""

from .system_detector import SystemWindowDetector
from .edge_detector import EdgeDetector
from .content_detector import ContentDetector
from .validator import ScreenshotValidator
from .utils import ScreenshotUtils


class DetectionStrategy:
    """检测策略管理器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.utils = ScreenshotUtils()
        self.system_detector = SystemWindowDetector()
        self.edge_detector = EdgeDetector(window_manager)
        self.content_detector = ContentDetector(window_manager)
        self.validator = ScreenshotValidator()
    
    def detect_miniprogram_bounds(self):
        """智能检测小程序内容边界（多重检测策略）"""
        print("\n🔍 开始智能检测小程序内容边界...")
        
        # 清理旧截图
        self.utils.clean_old_screenshots()
        
        # 方法1: 系统窗口检测（最精确，类似Snipaste）
        print("\n🏆 尝试方法1: 系统级窗口检测")
        bounds = self.system_detector.detect_miniprogram_window()
        if bounds and self.validator.validate_miniprogram_bounds(bounds):
            print(f"✅ 系统窗口检测成功，直接使用系统检测结果")
            return bounds
        
        # 如果没有检测到微信窗口，尝试其他方法
        if not self.window_manager.wechat_window_bounds:
            print("⚠️ 未找到微信窗口，尝试重新检测...")
            if not self.window_manager.find_and_setup_wechat_window():
                print("❌ 无法找到微信窗口，截图功能不可用")
                return None
        
        # 方法2: 内容密度分析检测
        print("\n📊 尝试方法2: 内容密度分析")
        bounds = self.content_detector.detect_miniprogram_content()
        if bounds and self.validator.validate_miniprogram_bounds(bounds):
            print(f"✅ 内容密度检测成功")
            return bounds
        
        # 方法3: 边缘检测方法
        print("\n🔍 尝试方法3: 边缘检测")
        bounds = self.edge_detector.detect_miniprogram_edges()
        if bounds and self.validator.validate_miniprogram_bounds(bounds):
            print(f"✅ 边缘检测成功")
            return bounds
        
        # 所有方法都失败，使用兜底方案
        print("\n⚠️ 所有智能检测方法都失败，使用保守兜底方案")
        return self._fallback_detection()
    
    def _fallback_detection(self):
        """兜底检测方案"""
        if not self.window_manager.wechat_window_bounds:
            return None
        
        wechat_bounds = self.window_manager.wechat_window_bounds
        
        # 使用微信窗口的中心区域作为小程序区域（保守估计）
        fallback_width = min(414, wechat_bounds['width'] - 100)
        fallback_height = min(780, wechat_bounds['height'] - 100)
        
        fallback_x = wechat_bounds['x'] + (wechat_bounds['width'] - fallback_width) // 2
        fallback_y = wechat_bounds['y'] + (wechat_bounds['height'] - fallback_height) // 2
        
        fallback_bounds = {
            'x': fallback_x,
            'y': fallback_y,
            'width': fallback_width,
            'height': fallback_height
        }
        
        print(f"🛡️ 兜底方案: {self.utils.format_bounds_info(fallback_bounds)}")
        return fallback_bounds 