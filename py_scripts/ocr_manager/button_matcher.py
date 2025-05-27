#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按钮匹配器
负责匹配特定的按钮文案和计算点击位置
"""

import re
from difflib import SequenceMatcher


class ButtonMatcher:
    """按钮匹配器类"""
    
    def __init__(self):
        """初始化按钮匹配器"""
        self.target_buttons = [
            "核心皮肤",
            "入坑到入土", 
            "宝石图鉴",
            "技能前置",
            "子弹前置",
            "百分比伤害",
            "技能升级",
            "佣兵图鉴",
            "城墙数据",
            "精英怪图鉴",
            "历练大厅",
            "寰球攻略"
        ]
        self.similarity_threshold = 0.8  # 相似度阈值
    
    def find_target_buttons(self, text_items):
        """从文字识别结果中找到目标按钮"""
        matched_buttons = []
        
        for target_button in self.target_buttons:
            best_match = self._find_best_match(target_button, text_items)
            if best_match:
                matched_buttons.append({
                    'target': target_button,
                    'matched_text': best_match['text'],
                    'center': best_match['center'],
                    'confidence': best_match['confidence'],
                    'similarity': best_match.get('similarity', 1.0),
                    'bbox': best_match['bbox']
                })
                print(f"✅ 找到按钮: {target_button} -> {best_match['text']}")
        
        # 按照目标按钮的顺序排序
        matched_buttons.sort(key=lambda x: self.target_buttons.index(x['target']))
        
        print(f"🎯 总共匹配到 {len(matched_buttons)} 个目标按钮")
        return matched_buttons
    
    def _find_best_match(self, target_text, text_items):
        """为目标文字找到最佳匹配"""
        best_match = None
        best_similarity = 0
        
        for item in text_items:
            detected_text = self._clean_text(item['text'])
            
            # 完全匹配优先
            if detected_text == target_text:
                item['similarity'] = 1.0
                return item
            
            # 包含匹配
            if target_text in detected_text or detected_text in target_text:
                similarity = self._calculate_similarity(target_text, detected_text)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = item.copy()
                    best_match['similarity'] = similarity
            
            # 模糊匹配
            similarity = self._calculate_similarity(target_text, detected_text)
            if similarity > best_similarity and similarity >= self.similarity_threshold:
                best_similarity = similarity
                best_match = item.copy()
                best_match['similarity'] = similarity
        
        return best_match
    
    def _clean_text(self, text):
        """清理文字，去除空格和特殊字符"""
        # 去除所有空格和特殊字符，只保留中文、英文、数字
        cleaned = re.sub(r'[^\w\u4e00-\u9fff]', '', text)
        return cleaned.strip()
    
    def _calculate_similarity(self, text1, text2):
        """计算两个文字的相似度"""
        # 清理文字
        clean1 = self._clean_text(text1).lower()
        clean2 = self._clean_text(text2).lower()
        
        # 使用SequenceMatcher计算相似度
        similarity = SequenceMatcher(None, clean1, clean2).ratio()
        return similarity
    
    def get_unmatched_buttons(self, matched_buttons):
        """获取未匹配到的按钮列表"""
        matched_targets = [btn['target'] for btn in matched_buttons]
        unmatched = [btn for btn in self.target_buttons if btn not in matched_targets]
        
        if unmatched:
            print(f"⚠️ 未匹配到的按钮: {', '.join(unmatched)}")
        
        return unmatched
    
    def validate_button_position(self, button, bounds):
        """验证按钮位置是否在有效范围内"""
        center_x, center_y = button['center']
        
        # 检查是否在小程序边界内
        if (bounds['x'] <= center_x <= bounds['x'] + bounds['width'] and
            bounds['y'] <= center_y <= bounds['y'] + bounds['height']):
            return True
        
        print(f"⚠️ 按钮 {button['target']} 位置超出边界")
        return False
    
    def filter_valid_buttons(self, matched_buttons, bounds):
        """过滤有效的按钮"""
        valid_buttons = []
        
        for button in matched_buttons:
            if self.validate_button_position(button, bounds):
                valid_buttons.append(button)
        
        print(f"✅ 验证通过的按钮: {len(valid_buttons)} 个")
        return valid_buttons
    
    def get_click_position(self, button, bounds):
        """获取按钮的绝对点击位置"""
        center_x, center_y = button['center']
        
        # 转换为绝对坐标
        absolute_x = bounds['x'] + center_x
        absolute_y = bounds['y'] + center_y
        
        return (absolute_x, absolute_y) 