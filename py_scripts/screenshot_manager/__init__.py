#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图管理器模块
负责截图、滚动截图、图片处理等功能
"""

from .core import ScreenshotManager
from .system_detector import SystemWindowDetector
from .edge_detector import EdgeDetector
from .content_detector import ContentDetector
from .validator import ScreenshotValidator
from .utils import ScreenshotUtils
from .window_analyzer import WindowContentAnalyzer
from .detection_strategy import DetectionStrategy
from .quality_checker import QualityChecker
from .content_analysis import ContentAnalyzer
from .content_region_selector import ContentRegionSelector
from .edge_analysis import EdgeAnalyzer
from .contour_processor import ContourProcessor
from .ui_feature_detector import UIFeatureDetector

__all__ = [
    'ScreenshotManager',
    'SystemWindowDetector', 
    'EdgeDetector',
    'ContentDetector',
    'ScreenshotValidator',
    'ScreenshotUtils',
    'WindowContentAnalyzer',
    'DetectionStrategy',
    'QualityChecker',
    'ContentAnalyzer',
    'ContentRegionSelector',
    'EdgeAnalyzer',
    'ContourProcessor',
    'UIFeatureDetector'
]

__version__ = '1.0.0' 