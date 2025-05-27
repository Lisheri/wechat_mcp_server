#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文字检测器
使用OCR技术识别图片中的文字内容
"""

import cv2
import numpy as np
from PIL import Image, ImageGrab
import easyocr
import re


class TextDetector:
    """文字检测器类"""
    
    def __init__(self):
        """初始化OCR检测器"""
        self.reader = None
        self._init_ocr_reader()
    
    def _init_ocr_reader(self):
        """初始化EasyOCR读取器"""
        try:
            # 支持中文和英文，强制使用CPU避免MPS警告
            self.reader = easyocr.Reader(['ch_sim', 'en'], gpu=False, verbose=False)
            print("✅ OCR引擎初始化成功 (CPU模式)")
        except Exception as e:
            print(f"❌ OCR引擎初始化失败: {e}")
            print("💡 请安装easyocr: pip install easyocr")
            self.reader = None
    
    def detect_text_from_image(self, image_path):
        """从图片文件检测文字"""
        if not self.reader:
            print("❌ OCR引擎未初始化")
            return []
        
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                print(f"❌ 无法读取图片: {image_path}")
                return []
            
            # 进行OCR识别
            results = self.reader.readtext(image)
            
            # 解析结果
            text_items = []
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # 置信度过滤
                    # 计算边界框中心点
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    center_x = int(sum(x_coords) / len(x_coords))
                    center_y = int(sum(y_coords) / len(y_coords))
                    
                    text_items.append({
                        'text': text.strip(),
                        'confidence': confidence,
                        'bbox': bbox,
                        'center': (center_x, center_y),
                        'width': max(x_coords) - min(x_coords),
                        'height': max(y_coords) - min(y_coords)
                    })
            
            print(f"🔍 检测到 {len(text_items)} 个文字区域")
            return text_items
            
        except Exception as e:
            print(f"❌ 文字检测失败: {e}")
            return []
    
    def detect_text_from_bounds(self, bounds):
        """从指定区域截图并检测文字"""
        try:
            # 截取指定区域
            screenshot = ImageGrab.grab(bbox=(
                bounds['x'], bounds['y'],
                bounds['x'] + bounds['width'],
                bounds['y'] + bounds['height']
            ))
            
            # 保存临时图片
            temp_path = "/tmp/ocr_temp.png"
            screenshot.save(temp_path)
            
            # 检测文字
            return self.detect_text_from_image(temp_path)
            
        except Exception as e:
            print(f"❌ 区域文字检测失败: {e}")
            return []
    
    def preprocess_image_for_ocr(self, image_path):
        """预处理图片以提高OCR准确率"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 高斯模糊去噪
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            
            # 自适应阈值处理
            thresh = cv2.adaptiveThreshold(
                blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # 保存预处理后的图片
            processed_path = image_path.replace('.png', '_processed.png')
            cv2.imwrite(processed_path, thresh)
            
            return processed_path
            
        except Exception as e:
            print(f"❌ 图片预处理失败: {e}")
            return image_path
    
    def clean_text(self, text):
        """清理文字内容"""
        # 去除特殊字符和空格
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        return cleaned.strip()
    
    def is_valid_text(self, text, min_length=2):
        """检查文字是否有效"""
        if not text or len(text) < min_length:
            return False
        
        # 检查是否包含中文或英文
        if re.search(r'[\u4e00-\u9fff]', text) or re.search(r'[a-zA-Z]', text):
            return True
        
        return False 