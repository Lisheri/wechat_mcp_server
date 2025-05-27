#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能导航器
负责主页按钮检测和智能页面导航
"""

import time


class SmartNavigator:
    """智能导航器类"""
    
    def __init__(self, button_detector, button_navigator, window_manager):
        """初始化智能导航器"""
        self.button_detector = button_detector
        self.button_navigator = button_navigator
        self.window_manager = window_manager
    
    def detect_main_page_buttons(self, bounds):
        """检测主页面的目标按钮"""
        print("🔍 开始检测主页面按钮...")
        
        # 确保在主页面
        if not self.button_detector.check_is_main_page(bounds):
            print("⚠️ 当前不在主页面，尝试返回主页")
            if not self.button_navigator.ensure_main_page(bounds):
                print("❌ 无法确保回到主页面")
                return []
        
        # 确保聚焦到小程序区域
        self.window_manager.focus_mini_program_area()
        time.sleep(1)
        
        # 检测按钮
        target_buttons = self.button_detector.detect_buttons_in_bounds(bounds)
        
        if target_buttons:
            print(f"✅ 在主页面检测到 {len(target_buttons)} 个目标按钮:")
            for i, button in enumerate(target_buttons):
                print(f"  {i+1}. {button['target']} (置信度: {button['confidence']:.2f})")
        else:
            print("❌ 未检测到任何目标按钮")
            # 保存调试信息
            self.button_detector.save_detection_debug_info()
        
        return target_buttons
    
    def navigate_to_button_page(self, button, bounds):
        """导航到指定按钮页面"""
        print(f"🧭 导航到页面: {button['target']}")
        
        try:
            # 确保在主页面
            if not self.button_navigator.is_on_main_page():
                print("⚠️ 不在主页面，先返回主页")
                if not self.button_navigator.ensure_main_page(bounds):
                    return False
            
            # 点击按钮
            if self.button_navigator.click_button(button, bounds):
                # 等待页面加载
                time.sleep(2)
                
                # 验证是否成功进入内页（检查是否有返回箭头）
                is_still_main_page = self.button_detector.check_is_main_page(bounds)
                
                if not is_still_main_page:
                    print(f"✅ 成功进入内页: {button['target']}")
                    return True
                else:
                    print(f"⚠️ 返回按钮检测认为仍在主页，但强制继续执行内页截图")
                    print(f"📸 点击已执行，假设成功进入内页: {button['target']}")
                    # 即使检测认为在主页，也强制返回True，继续执行内页截图
                    return True
            else:
                print(f"❌ 点击按钮失败: {button['target']}")
                return False
                
        except Exception as e:
            print(f"❌ 导航失败: {e}")
            return False
    
    def return_to_main_page(self, bounds):
        """返回主页面"""
        print("🔙 返回主页面...")
        
        try:
            # 检查是否已经在主页
            if self.button_detector.check_is_main_page(bounds):
                print("✅ 已在主页面")
                return True
            
            # 尝试多种返回方法
            max_attempts = 3
            
            for attempt in range(max_attempts):
                print(f"🔄 返回尝试 {attempt + 1}/{max_attempts}")
                
                # 方法1: 点击返回按钮
                if self.button_navigator.return_to_main_page(bounds):
                    # 等待页面加载
                    time.sleep(2)
                    
                    # 验证是否成功返回主页
                    if self.button_detector.check_is_main_page(bounds):
                        print("✅ 成功返回主页面")
                        return True
                    else:
                        print(f"⚠️ 返回尝试 {attempt + 1} 未成功，继续尝试...")
                else:
                    print(f"❌ 返回按钮点击失败，尝试 {attempt + 1}")
                
                # 如果第一次失败，尝试其他方法
                if attempt < max_attempts - 1:
                    # 方法2: 尝试点击左上角区域
                    print("🔄 尝试点击左上角返回区域...")
                    self._try_click_back_area(bounds)
                    time.sleep(2)
                    
                    if self.button_detector.check_is_main_page(bounds):
                        print("✅ 通过左上角点击成功返回主页")
                        return True
            
            # 所有尝试都失败了
            print("⚠️ 多次返回尝试失败，但继续处理下一个按钮")
            print("💡 提示：手动检查是否需要返回主页")
            return False
                
        except Exception as e:
            print(f"❌ 返回主页失败: {e}")
            return False
    
    def _try_click_back_area(self, bounds):
        """尝试点击返回区域"""
        try:
            # 计算左上角返回区域
            x, y, width, height = bounds
            back_x = x + 30  # 左上角偏移30像素
            back_y = y + 60  # 顶部偏移60像素
            
            print(f"🎯 尝试点击返回区域: ({back_x}, {back_y})")
            
            # 点击左上角区域
            import pyautogui
            pyautogui.click(back_x, back_y)
            
        except Exception as e:
            print(f"⚠️ 点击返回区域失败: {e}")
    
    def get_navigation_status(self):
        """获取导航状态"""
        return {
            'current_page': self.button_navigator.get_current_page(),
            'is_on_main_page': self.button_navigator.is_on_main_page(),
            'navigation_history': len(self.button_navigator.get_navigation_history())
        }
    
    def reset_navigation_state(self):
        """重置导航状态"""
        self.button_navigator.clear_navigation_history()
        self.button_detector.reset_detection_cache()
        print("🔄 已重置导航状态")
    
    def ensure_ready_for_detection(self, bounds):
        """确保准备好进行按钮检测"""
        print("🎯 准备按钮检测环境...")
        
        # 1. 确保在主页面
        if not self.button_detector.check_is_main_page(bounds):
            print("📱 确保回到主页面...")
            if not self.button_navigator.ensure_main_page(bounds):
                return False
        
        # 2. 确保聚焦到小程序
        self.window_manager.focus_mini_program_area()
        time.sleep(1)
        
        # 3. 重置检测缓存
        self.button_detector.reset_detection_cache()
        
        print("✅ 检测环境准备完成")
        return True
    
    def batch_process_buttons(self, target_buttons, bounds, process_callback):
        """批量处理按钮"""
        if not target_buttons:
            print("❌ 没有按钮需要处理")
            return []
        
        results = []
        
        for i, button in enumerate(target_buttons):
            print(f"\n🎯 处理按钮 {i+1}/{len(target_buttons)}: {button['target']}")
            
            try:
                # 导航到按钮页面
                if self.navigate_to_button_page(button, bounds):
                    # 执行处理回调
                    result = process_callback(button)
                    results.append({
                        'button': button,
                        'success': True,
                        'result': result
                    })
                    
                    # 返回主页
                    self.return_to_main_page(bounds)
                else:
                    results.append({
                        'button': button,
                        'success': False,
                        'error': '导航失败'
                    })
                    
            except Exception as e:
                print(f"❌ 处理按钮时出错: {e}")
                results.append({
                    'button': button,
                    'success': False,
                    'error': str(e)
                })
        
        return results 