#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置文件
允许用户预设小程序名称和其他配置选项
"""

# 小程序配置
MINI_PROGRAM_CONFIG = {
    # 默认小程序名称
    'default_app_name': '微信小程序',
    
    # 预设的小程序名称列表（常用的小程序）
    'preset_apps': [
        '微信小程序',
        '向僵尸小助手',
        '微信读书',
        '腾讯文档',
        '小程序示例',
    ],
    
    # 是否跳过输入直接使用默认名称
    'skip_input': False,
    
    # 是否启用详细日志
    'verbose_logging': True,
    
    # 输入超时时间（秒）
    'input_timeout': 30,
}

# 爬虫行为配置
CRAWLER_BEHAVIOR = {
    # 是否在开始前显示配置信息
    'show_config_info': True,
    
    # 是否自动检测并使用最佳窗口
    'auto_detect_window': True,
    
    # 错误重试次数
    'max_retries': 3,
    
    # 是否保存调试截图
    'save_debug_screenshots': True,
}

def get_app_name_from_config():
    """从配置文件获取应用名称"""
    if MINI_PROGRAM_CONFIG['skip_input']:
        return MINI_PROGRAM_CONFIG['default_app_name']
    return None

def get_preset_apps():
    """获取预设应用列表"""
    return MINI_PROGRAM_CONFIG['preset_apps']

def is_verbose_logging():
    """是否启用详细日志"""
    return MINI_PROGRAM_CONFIG['verbose_logging']

def get_input_timeout():
    """获取输入超时时间"""
    return MINI_PROGRAM_CONFIG['input_timeout'] 