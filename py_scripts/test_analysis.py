#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试截图分析功能
"""

import os
import sys
from analysis_client import AnalysisClient

def test_screenshot_analysis():
    """测试截图分析功能"""
    print("🧪 测试截图分析功能...")
    
    # 创建分析客户端
    client = AnalysisClient()
    
    # 检查服务器健康状态
    if not client.check_server_health():
        print("❌ 服务器连接失败，请确保服务器正在运行")
        return False
    
    # 查找测试图片
    test_images = [
        "../crawl_results/screenshots/full_page_1748260130.png",
        "../crawl_results/screenshots/主页面_normal.png",
        "../crawl_results/screenshots/主页面_full_page.png"
    ]
    
    test_image = None
    for img in test_images:
        if os.path.exists(img):
            test_image = img
            break
    
    if not test_image:
        print("❌ 未找到测试图片")
        print("💡 请先运行爬虫生成截图")
        return False
    
    print(f"📸 使用测试图片: {test_image}")
    
    # 分析截图
    result = client.analyze_screenshot(test_image, "测试页面")
    
    if result:
        print("✅ 截图分析成功！")
        print(f"📊 分析结果:")
        print(f"   - 文本元素: {len(result.get('extractedTexts', []))} 个")
        print(f"   - 按钮: {len(result.get('detectedButtons', []))} 个")
        print(f"   - 图标: {len(result.get('detectedIcons', []))} 个")
        
        # 显示检测到的按钮
        buttons = result.get('detectedButtons', [])
        if buttons:
            print(f"\n🔘 检测到的按钮:")
            for i, btn in enumerate(buttons[:5]):  # 只显示前5个
                print(f"   {i+1}. {btn.get('text', '未知')}")
        
        return True
    else:
        print("❌ 截图分析失败")
        return False

if __name__ == "__main__":
    success = test_screenshot_analysis()
    sys.exit(0 if success else 1) 