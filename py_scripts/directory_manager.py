#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目录管理器
负责创建和管理不同按钮对应的截图目录
"""

import os
import re
from datetime import datetime
from config import CrawlerConfig


class DirectoryManager:
    """目录管理器类"""
    
    def __init__(self):
        """初始化目录管理器"""
        self.base_screenshots_dir = CrawlerConfig.SCREENSHOTS_DIR
        self.current_button_dir = None
        self.created_dirs = []
    
    def create_button_directory(self, button_name):
        """为指定按钮创建目录"""
        # 清理按钮名称，确保可以作为目录名
        safe_name = self._make_safe_dirname(button_name)
        
        # 创建按钮专用目录
        button_dir = os.path.join(self.base_screenshots_dir, safe_name)
        
        try:
            os.makedirs(button_dir, exist_ok=True)
            self.current_button_dir = button_dir
            self.created_dirs.append(button_dir)
            
            print(f"📁 创建按钮目录: {safe_name}")
            return button_dir
            
        except Exception as e:
            print(f"❌ 创建目录失败: {e}")
            return None
    
    def get_button_screenshot_path(self, filename):
        """获取当前按钮目录下的截图路径"""
        if not self.current_button_dir:
            print("⚠️ 当前按钮目录未设置")
            return os.path.join(self.base_screenshots_dir, filename)
        
        return os.path.join(self.current_button_dir, filename)
    
    def _make_safe_dirname(self, name):
        """将按钮名称转换为安全的目录名"""
        # 去除或替换不安全的字符
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        safe_name = safe_name.strip()
        
        # 如果是空字符串，使用默认名称
        if not safe_name:
            safe_name = "unknown_button"
        
        return safe_name
    
    def switch_to_button_directory(self, button_name):
        """切换到指定按钮的目录"""
        safe_name = self._make_safe_dirname(button_name)
        button_dir = os.path.join(self.base_screenshots_dir, safe_name)
        
        if os.path.exists(button_dir):
            self.current_button_dir = button_dir
            print(f"📂 切换到按钮目录: {safe_name}")
            return True
        else:
            print(f"❌ 按钮目录不存在: {safe_name}")
            return False
    
    def list_button_directories(self):
        """列出所有按钮目录"""
        if not os.path.exists(self.base_screenshots_dir):
            return []
        
        dirs = []
        for item in os.listdir(self.base_screenshots_dir):
            item_path = os.path.join(self.base_screenshots_dir, item)
            if os.path.isdir(item_path):
                dirs.append(item)
        
        return dirs
    
    def get_button_screenshot_count(self, button_name=None):
        """获取按钮目录中的截图数量"""
        if button_name:
            safe_name = self._make_safe_dirname(button_name)
            target_dir = os.path.join(self.base_screenshots_dir, safe_name)
        else:
            target_dir = self.current_button_dir
        
        if not target_dir or not os.path.exists(target_dir):
            return 0
        
        count = 0
        for filename in os.listdir(target_dir):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                count += 1
        
        return count
    
    def cleanup_empty_directories(self):
        """清理空的按钮目录"""
        if not os.path.exists(self.base_screenshots_dir):
            return
        
        cleaned_count = 0
        for item in os.listdir(self.base_screenshots_dir):
            item_path = os.path.join(self.base_screenshots_dir, item)
            if os.path.isdir(item_path):
                # 检查是否为空目录
                if not os.listdir(item_path):
                    try:
                        os.rmdir(item_path)
                        cleaned_count += 1
                        print(f"🗑️ 清理空目录: {item}")
                    except Exception as e:
                        print(f"⚠️ 清理目录失败: {item} - {e}")
        
        if cleaned_count > 0:
            print(f"✅ 清理了 {cleaned_count} 个空目录")
    
    def get_directory_summary(self):
        """获取目录结构摘要"""
        summary = {
            'total_directories': 0,
            'total_screenshots': 0,
            'directories': {}
        }
        
        if not os.path.exists(self.base_screenshots_dir):
            return summary
        
        for item in os.listdir(self.base_screenshots_dir):
            item_path = os.path.join(self.base_screenshots_dir, item)
            if os.path.isdir(item_path):
                summary['total_directories'] += 1
                
                # 统计该目录下的截图数量
                screenshot_count = 0
                for filename in os.listdir(item_path):
                    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                        screenshot_count += 1
                
                summary['directories'][item] = screenshot_count
                summary['total_screenshots'] += screenshot_count
        
        return summary
    
    def create_timestamp_subdirectory(self, button_name):
        """为按钮创建带时间戳的子目录"""
        safe_name = self._make_safe_dirname(button_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        subdir_name = f"{safe_name}_{timestamp}"
        subdir_path = os.path.join(self.base_screenshots_dir, subdir_name)
        
        try:
            os.makedirs(subdir_path, exist_ok=True)
            self.current_button_dir = subdir_path
            
            print(f"📁 创建时间戳目录: {subdir_name}")
            return subdir_path
            
        except Exception as e:
            print(f"❌ 创建时间戳目录失败: {e}")
            return None 