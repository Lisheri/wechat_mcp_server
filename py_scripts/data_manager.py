#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理器
负责数据收集、存储和报告生成
"""

import json
import os
import time
from datetime import datetime
from config import CrawlerConfig

class DataManager:
    """数据管理器"""
    
    def __init__(self):
        self.crawl_data = {
            "crawl_info": {
                "start_time": datetime.now().isoformat(),
                "app_name": "",
                "total_pages": 0,
                "total_buttons": 0,
                "crawl_duration": 0
            },
            "pages": [],
            "navigation_map": {},
            "feature_summary": {}
        }
        self.visited_buttons = set()
        self.start_time = time.time()
    
    def set_app_name(self, app_name):
        """设置应用名称"""
        self.crawl_data['crawl_info']['app_name'] = app_name
    
    def add_page_data(self, page_data):
        """添加页面数据"""
        self.crawl_data['pages'].append(page_data)
    
    def add_navigation_mapping(self, button_text, page_name):
        """添加导航映射"""
        self.crawl_data['navigation_map'][button_text] = page_name
    
    def add_visited_button(self, button_id):
        """添加已访问的按钮"""
        self.visited_buttons.add(button_id)
    
    def is_button_visited(self, button_id):
        """检查按钮是否已访问"""
        return button_id in self.visited_buttons
    
    def finalize_crawl_data(self):
        """完成爬取数据的最终处理"""
        end_time = time.time()
        self.crawl_data['crawl_info']['end_time'] = datetime.now().isoformat()
        self.crawl_data['crawl_info']['crawl_duration'] = round(end_time - self.start_time, 2)
        self.crawl_data['crawl_info']['total_pages'] = len(self.crawl_data['pages'])
        self.crawl_data['crawl_info']['total_buttons'] = len(self.visited_buttons)
        
        # 生成功能总结
        self._generate_feature_summary()
    
    def _generate_feature_summary(self):
        """生成功能总结"""
        summary = {
            'total_unique_features': set(),
            'feature_categories': {},
            'page_types': {},
            'navigation_depth': 0,
            'color_themes': [],
            'layout_patterns': []
        }
        
        for page in self.crawl_data['pages']:
            features = page.get('extracted_features', {})
            
            # 收集功能类型
            for func in features.get('functionality', []):
                func_type = func.get('type', '')
                if func_type:
                    summary['total_unique_features'].add(func_type)
                    if func_type not in summary['feature_categories']:
                        summary['feature_categories'][func_type] = 0
                    summary['feature_categories'][func_type] += 1
            
            # 分析页面类型
            page_name = page.get('page_name', '')
            page_type = self._classify_page_type(page_name)
            
            if page_type not in summary['page_types']:
                summary['page_types'][page_type] = 0
            summary['page_types'][page_type] += 1
            
            # 收集颜色主题
            colors = features.get('colors', [])
            if colors:
                primary_color = colors[0].get('color', '')
                if primary_color and primary_color not in summary['color_themes']:
                    summary['color_themes'].append(primary_color)
        
        # 转换set为list以便JSON序列化
        summary['total_unique_features'] = list(summary['total_unique_features'])
        summary['feature_count'] = len(summary['total_unique_features'])
        
        self.crawl_data['feature_summary'] = summary
    
    def _classify_page_type(self, page_name):
        """分类页面类型"""
        if '主页' in page_name:
            return '主页面'
        elif '列表' in page_name or '目录' in page_name:
            return '列表页'
        elif '详情' in page_name or '详细' in page_name:
            return '详情页'
        else:
            return '功能页'
    
    def save_results(self):
        """保存爬取结果"""
        # 保存完整的JSON数据
        json_path = os.path.join(
            CrawlerConfig.OUTPUT_DIR, 
            CrawlerConfig.get_timestamp_filename("crawl_results", ".json")
        )
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.crawl_data, f, ensure_ascii=False, indent=2)
        
        # 保存简化的报告
        report_path = os.path.join(
            CrawlerConfig.OUTPUT_DIR, 
            CrawlerConfig.get_timestamp_filename("crawl_report", ".txt")
        )
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_text_report())
        
        print(f"💾 爬取结果已保存:")
        print(f"   📄 完整数据: {json_path}")
        print(f"   📋 文本报告: {report_path}")
        
        return json_path, report_path
    
    def _generate_text_report(self):
        """生成文本格式的报告"""
        report = []
        report.append("=" * 60)
        report.append("微信小程序爬取报告")
        report.append("=" * 60)
        
        info = self.crawl_data['crawl_info']
        report.append(f"应用名称: {info['app_name']}")
        report.append(f"爬取时间: {info['start_time']}")
        report.append(f"总页面数: {info['total_pages']}")
        report.append(f"总按钮数: {info['total_buttons']}")
        report.append(f"爬取耗时: {info['crawl_duration']}秒")
        report.append("")
        
        # 功能总结
        summary = self.crawl_data['feature_summary']
        report.append("功能总结:")
        report.append(f"  发现功能类型: {summary['feature_count']}种")
        for func_type, count in summary['feature_categories'].items():
            report.append(f"    - {func_type}: {count}个")
        report.append("")
        
        # 页面详情
        report.append("页面详情:")
        for page in self.crawl_data['pages']:
            report.append(f"  📄 {page['page_name']}")
            features = page['extracted_features']
            report.append(f"    - 文本元素: {len(features['text_elements'])}个")
            report.append(f"    - 按钮: {len(features['buttons'])}个")
            report.append(f"    - 图标: {len(features['icons'])}个")
            report.append(f"    - 功能: {len(features['functionality'])}个")
            report.append("")
        
        return "\n".join(report)
    
    def get_crawl_stats(self):
        """获取爬取统计信息"""
        return {
            'total_pages': len(self.crawl_data['pages']),
            'total_buttons': len(self.visited_buttons),
            'duration': round(time.time() - self.start_time, 2)
        } 