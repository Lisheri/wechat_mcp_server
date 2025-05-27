import time

class PageCrawler:
    def crawl_inner_page(self, button_name, button_dir):
        """爬取内页内容"""
        print(f"📄 开始爬取内页: {button_name}")
        
        # 确保环境已设置
        if not hasattr(self.window_manager, '_mini_program_bounds') or not self.window_manager._mini_program_bounds:
            print("🔧 设置小程序环境...")
            self.window_manager.setup_mini_program_environment()
        
        # 等待页面加载
        time.sleep(2)
        
        # 强制执行内页截图（不依赖页面类型检测）
        print(f"📸 强制执行内页截图（不依赖返回按钮检测）")
        
        # 先拍一张初始截图
        initial_screenshot = f"{button_dir}/page_001.png"
        if self.screenshot_manager.take_screenshot(initial_screenshot):
            print(f"✅ 初始截图已保存: {initial_screenshot}")
        
        # 执行滚动截图
        scroll_count = self._perform_smart_scrolling(button_dir)
        
        if scroll_count > 0:
            print(f"✅ 滚动截图完成，共 {scroll_count} 张截图")
        else:
            print("ℹ️ 未进行滚动截图（可能已在底部）")
        
        # 现在尝试返回主页
        print(f"🔙 尝试返回主页...")
        return_success = self._return_to_main_page()
        
        if return_success:
            print(f"✅ 成功返回主页")
            # 等待主页加载
            time.sleep(2)
        else:
            print(f"⚠️ 返回主页可能失败，尝试其他方法...")
            # 尝试点击更多位置来返回
            self._try_alternative_return_methods()
        
        return True 