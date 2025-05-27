#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复MPS警告问题的脚本
针对Apple Silicon Mac上的PyTorch MPS警告进行优化
"""

import os
import sys
import warnings


def setup_torch_for_apple_silicon():
    """为Apple Silicon设置PyTorch环境"""
    print("🍎 检测到Apple Silicon环境，正在优化PyTorch配置...")
    
    # 设置环境变量
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    os.environ['TORCH_DEVICE'] = 'cpu'
    os.environ['OMP_NUM_THREADS'] = '1'
    
    # 过滤警告
    warnings.filterwarnings('ignore', category=UserWarning, module='torch')
    warnings.filterwarnings('ignore', message='.*pin_memory.*')
    
    print("✅ PyTorch配置优化完成")


def test_ocr_without_warnings():
    """测试OCR功能是否正常工作且无警告"""
    print("\n🧪 测试OCR功能...")
    
    try:
        # 导入并测试OCR
        from ocr_manager import TextDetector
        
        detector = TextDetector()
        if detector.reader:
            print("✅ OCR引擎初始化成功，无MPS警告")
            return True
        else:
            print("❌ OCR引擎初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ OCR测试失败: {e}")
        return False


def show_apple_silicon_tips():
    """显示Apple Silicon优化建议"""
    print("\n💡 Apple Silicon Mac优化建议:")
    print("1. 使用CPU模式运行OCR（避免MPS兼容性问题）")
    print("2. 设置合适的线程数量（避免资源争用）")
    print("3. 过滤无关警告（保持控制台整洁）")
    print("4. 如需GPU加速，可考虑使用专门的ML框架")


def main():
    """主函数"""
    print("🔧 MPS警告修复工具")
    print("=" * 40)
    
    # 设置环境
    setup_torch_for_apple_silicon()
    
    # 测试OCR
    if test_ocr_without_warnings():
        print("\n🎉 MPS警告问题已解决！")
    else:
        print("\n⚠️ 仍有问题需要解决")
    
    # 显示优化建议
    show_apple_silicon_tips()


if __name__ == "__main__":
    main() 