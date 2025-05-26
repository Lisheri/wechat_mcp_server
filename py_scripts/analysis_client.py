#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析客户端
负责与MCP服务器通信，进行图像分析
"""

import base64
import requests
from config import CrawlerConfig

class AnalysisClient:
    """分析客户端"""
    
    def __init__(self):
        self.server_url = CrawlerConfig.SERVER_URL
    
    def check_server_health(self):
        """检查MCP服务器状态"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                print("✅ MCP服务器连接正常")
                return True
            else:
                print(f"❌ MCP服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接到MCP服务器: {e}")
            return False
    
    def encode_image_to_base64(self, image_path):
        """将图片编码为Base64"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            print(f"❌ 图片编码失败: {e}")
            return None
    
    def analyze_screenshot(self, image_path, page_name="unknown"):
        """分析截图并获取页面信息"""
        print(f"🔍 正在分析页面: {page_name}")
        
        image_base64 = self.encode_image_to_base64(image_path)
        if not image_base64:
            return None
        
        # 构建分析请求
        request_data = {
            "screenshotBase64": image_base64,
            "analysisOptions": {
                "extractText": True,
                "detectButtons": True,
                "detectIcons": True,
                "analyzeLayout": True,
                "extractColors": True
            }
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/wechat-mini/analyze-screenshot",
                json=request_data,
                headers={'Content-Type': 'application/json'},
                timeout=CrawlerConfig.ANALYSIS_TIMEOUT
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print(f"✅ 页面分析完成: {page_name}")
                    return result['data']
                else:
                    print(f"❌ 页面分析失败: {result.get('message', '未知错误')}")
            else:
                print(f"❌ 服务器响应错误: {response.status_code}")
        except Exception as e:
            print(f"❌ 分析请求异常: {e}")
        
        return None
    
    def extract_page_features(self, analysis_data):
        """从分析数据中提取页面特征"""
        features = {
            'text_elements': [],
            'buttons': [],
            'icons': [],
            'layout': {},
            'colors': [],
            'functionality': []
        }
        
        if analysis_data:
            # 提取文本元素
            features['text_elements'] = [
                {
                    'text': text.get('text', ''),
                    'position': text.get('position', {}),
                    'confidence': text.get('confidence', 0)
                }
                for text in analysis_data.get('extractedTexts', [])
            ]
            
            # 提取按钮信息
            features['buttons'] = [
                {
                    'text': btn.get('text', ''),
                    'type': btn.get('type', ''),
                    'position': btn.get('position', {})
                }
                for btn in analysis_data.get('detectedButtons', [])
            ]
            
            # 提取图标信息
            features['icons'] = [
                {
                    'description': icon.get('description', ''),
                    'category': icon.get('category', ''),
                    'position': icon.get('position', {})
                }
                for icon in analysis_data.get('detectedIcons', [])
            ]
            
            # 提取布局信息
            features['layout'] = analysis_data.get('layoutInfo', {})
            
            # 提取颜色信息
            features['colors'] = analysis_data.get('colorPalette', [])
            
            # 分析功能性
            features['functionality'] = self._analyze_functionality(features['buttons'], features['icons'])
        
        return features
    
    def _analyze_functionality(self, buttons, icons):
        """分析页面功能性"""
        functionality = []
        
        # 基于按钮文本分析功能
        function_keywords = {
            '查询': ['查询', '搜索', '查找'],
            '计算': ['计算', '测算', '估算'],
            '设置': ['设置', '配置', '选项'],
            '分享': ['分享', '转发', '推荐'],
            '收藏': ['收藏', '保存', '添加'],
            '购买': ['购买', '支付', '下单'],
            '游戏': ['游戏', '娱乐', '玩法'],
            '工具': ['工具', '助手', '帮助'],
            '信息': ['信息', '详情', '介绍'],
            '社交': ['好友', '群组', '聊天']
        }
        
        for button in buttons:
            button_text = button.get('text', '')
            for func_type, keywords in function_keywords.items():
                if any(keyword in button_text for keyword in keywords):
                    functionality.append({
                        'type': func_type,
                        'element': button_text,
                        'element_type': 'button'
                    })
                    break
        
        return functionality 