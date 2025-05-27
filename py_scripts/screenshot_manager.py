#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图管理器
负责截图、滚动截图、图片处理等功能
"""

import os
import time
import pyautogui
import cv2
import numpy as np
from PIL import Image, ImageGrab
from skimage.metrics import structural_similarity as ssim
from config import CrawlerConfig
from scipy import ndimage
from scipy.signal import find_peaks
import pygetwindow as gw

class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, window_manager):
        self.window_manager = window_manager
        
    def detect_mini_program_content_bounds(self):
        """精确检测小程序内容边界（排除微信界面和黑色边框）"""
        if not self.window_manager.wechat_window_bounds:
            return None
        
        try:
            # 截取整个微信窗口
            wechat_bounds = self.window_manager.wechat_window_bounds
            full_screenshot = ImageGrab.grab(bbox=(
                wechat_bounds['x'],
                wechat_bounds['y'],
                wechat_bounds['x'] + wechat_bounds['width'],
                wechat_bounds['y'] + wechat_bounds['height']
            ))
            
            # 转换为OpenCV格式进行分析
            screenshot_cv = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            height, width = screenshot_cv.shape[:2]
            
            # 保存调试图像
            debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_detection.png")
            cv2.imwrite(debug_path, screenshot_cv)
            print(f"🐛 调试图像已保存: {debug_path}")
            
            # 方法1: 更严格的内容检测，排除边框和背景
            # 转换为HSV色彩空间
            hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
            
            # 检测有意义的内容区域（排除纯黑、纯白、纯灰等边框色彩）
            # 小程序内容通常有一定的饱和度和亮度变化
            lower_content = np.array([0, 10, 50])   # 最小饱和度10，最小亮度50
            upper_content = np.array([180, 255, 240])  # 最大亮度240，排除过亮的区域
            content_mask = cv2.inRange(hsv, lower_content, upper_content)
            
            # 同时检测浅色内容区域（如白色背景上的文字）
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # 使用边缘检测找到文字和UI元素
            edges = cv2.Canny(gray, 30, 100)
            
            # 膨胀边缘以连接相邻的文字和元素
            kernel = np.ones((3, 3), np.uint8)
            edges_dilated = cv2.dilate(edges, kernel, iterations=2)
            
            # 合并内容掩码和边缘检测结果
            combined_mask = cv2.bitwise_or(content_mask, edges_dilated)
            
            # 形态学操作，连接相邻的内容区域
            kernel = np.ones((5, 5), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            
            # 保存内容掩码调试图像
            mask_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_content_mask.png")
            cv2.imwrite(mask_debug_path, combined_mask)
            print(f"🐛 内容掩码图像已保存: {mask_debug_path}")
            
            # 方法2: 分析每一列的有效内容密度
            column_content_density = []
            for col in range(width):
                column_mask = combined_mask[:, col]
                content_pixels = np.sum(column_mask > 0)
                total_pixels = len(column_mask)
                density = content_pixels / total_pixels if total_pixels > 0 else 0
                column_content_density.append(density)
            
            # 使用更高的阈值来找到真正的内容区域
            high_density_threshold = 0.20  # 适度降低阈值，包含更多边缘内容
            high_density_columns = [i for i, density in enumerate(column_content_density) if density > high_density_threshold]
            
            if high_density_columns:
                # 找到连续的高密度区域
                content_regions = []
                start = high_density_columns[0]
                end = start
                
                for i in range(1, len(high_density_columns)):
                    if high_density_columns[i] - high_density_columns[i-1] <= 5:  # 增加允许的间隔
                        end = high_density_columns[i]
                    else:
                        if end - start > 250:  # 降低内容区域最小宽度要求
                            content_regions.append((start, end))
                        start = high_density_columns[i]
                        end = start
                
                # 添加最后一个区域
                if end - start > 250:
                    content_regions.append((start, end))
                
                print(f"🔍 检测到 {len(content_regions)} 个高密度内容区域: {content_regions}")
                
                # 选择最接近414像素宽度的区域
                best_region = None
                best_score = 0
                
                for start_col, end_col in content_regions:
                    region_width = end_col - start_col
                    width_diff = abs(region_width - 414)
                    
                    # 计算评分，更严格地评估宽度匹配
                    score = 0
                    if width_diff < 10:
                        score += 80
                    elif width_diff < 20:
                        score += 60
                    elif width_diff < 40:
                        score += 40
                    elif width_diff < 80:
                        score += 20
                    elif width_diff < 120:  # 扩展评分范围，包括较小的区域
                        score += 10
                    
                    # 位置评分（中心偏右的区域得分更高）
                    center_x = (start_col + end_col) // 2
                    if center_x > width * 0.3:
                        score += 15
                    
                    # 宽度合理性评分 - 调整范围以包括较小的合理区域
                    if 350 < region_width < 450:  # 包括327-450的范围
                        score += 25
                    elif 300 < region_width < 480:  # 更宽的合理范围
                        score += 15
                    
                    print(f"   内容区域: 列{start_col}-{end_col}, 宽度{region_width}, 评分{score}")
                    
                    if score > best_score:
                        best_score = score
                        best_region = (start_col, end_col)
                
                if best_region and best_score > 25:  # 降低评分阈值，接受合理的检测结果
                    left_boundary, right_boundary = best_region
                    content_width = right_boundary - left_boundary
                    
                    # 确定顶部和底部边界
                    row_content_density = []
                    for row in range(height):
                        row_mask = combined_mask[row, left_boundary:right_boundary]
                        content_pixels = np.sum(row_mask > 0)
                        total_pixels = len(row_mask)
                        density = content_pixels / total_pixels if total_pixels > 0 else 0
                        row_content_density.append(density)
                    
                    high_density_rows = [i for i, density in enumerate(row_content_density) if density > 0.10]  # 降低行密度阈值
                    
                    if high_density_rows:
                        top_boundary = min(high_density_rows)
                        bottom_boundary = max(high_density_rows)
                        content_height = bottom_boundary - top_boundary
                        
                        if content_height > 400:  # 降低高度要求
                            actual_bounds = {
                                'x': wechat_bounds['x'] + left_boundary,
                                'y': wechat_bounds['y'] + top_boundary,
                                'width': content_width,
                                'height': content_height
                            }
                            print(f"🎯 基于内容密度检测到小程序区域: {actual_bounds}")
                            print(f"   宽度与目标414像素的差距: {abs(content_width - 414)} 像素")
                            return actual_bounds
            
            # 如果高密度分析失败，回退到轮廓分析
            print("🔍 高密度分析未找到合适区域，回退到轮廓分析...")
            
            # 查找内容区域的轮廓
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            candidates = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 80000:  # 提高面积阈值
                    continue
                    
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = h / w
                
                # 更严格的小程序特征检查
                if aspect_ratio > 1.2 and w > 350 and h > 500:
                    # 检查内容区域的有效性
                    roi_mask = combined_mask[y:y+h, x:x+w]
                    content_ratio = np.sum(roi_mask > 0) / (w * h)
                    
                    if content_ratio > 0.2:  # 降低内容比例要求，因为使用了更严格的内容检测
                        score = 0
                        
                        # 宽度评分（接近414像素）
                        width_diff = abs(w - 414)
                        if width_diff < 15:
                            score += 70
                        elif width_diff < 30:
                            score += 50
                        elif width_diff < 50:
                            score += 30
                        
                        # 长宽比评分
                        if 1.5 < aspect_ratio < 2.2:
                            score += 25
                        
                        # 内容比例评分
                        if content_ratio > 0.4:
                            score += 20
                        elif content_ratio > 0.3:
                            score += 15
                        
                        candidates.append({
                            'bounds': (x, y, w, h),
                            'score': score,
                            'content_ratio': content_ratio,
                            'source': 'strict_contour_analysis'
                        })
                        
                        print(f"   严格轮廓候选区域: ({x},{y},{w},{h}) 评分:{score} 内容比例:{content_ratio:.2f}")
            
            # 选择最佳候选区域
            if candidates:
                best_candidate = max(candidates, key=lambda x: x['score'])
                
                if best_candidate['score'] > 40:
                    x, y, w, h = best_candidate['bounds']
                    actual_bounds = {
                        'x': wechat_bounds['x'] + x,
                        'y': wechat_bounds['y'] + y,
                        'width': w,
                        'height': h
                    }
                    print(f"🎯 精确检测到小程序内容区域: {actual_bounds}")
                    print(f"   评分: {best_candidate['score']}, 内容比例: {best_candidate['content_ratio']:.2f}")
                    print(f"   来源: {best_candidate['source']}")
                    return actual_bounds
                else:
                    print(f"⚠️ 候选区域评分过低: {best_candidate['score']}")
            else:
                print("⚠️ 未找到合适的候选区域")
            
        except Exception as e:
            print(f"⚠️ 精确检测失败: {e}")
            import traceback
            traceback.print_exc()
        
        return None
        
    def take_mini_program_screenshot(self, filename=None):
        """截取小程序区域的截图"""
        # 清理旧的截图文件
        if filename is None:
            self.clean_old_screenshots()
        
        # 优先尝试系统窗口检测方法（类似Snipaste）
        print("🔍 尝试系统窗口检测方法...")
        bounds = self.detect_miniprogram_by_system_windows()
        
        # 如果系统窗口检测失败，尝试边缘检测方法
        if not bounds:
            print("🔍 系统窗口检测失败，尝试边缘检测方法...")
            bounds = self.detect_miniprogram_by_edge_detection()
        
        # 如果边缘检测失败，使用内容密度分析
        if not bounds:
            print("🔍 边缘检测失败，尝试内容密度分析...")
            bounds = self.detect_mini_program_content_bounds()
        
        # 如果精确检测失败，使用设置的边界
        if not bounds:
            print("⚠️ 精确检测失败，使用设置的小程序区域...")
            bounds = self.window_manager.get_mini_program_bounds()
        
        # 如果还是没有边界，使用微信窗口的中心区域
        if not bounds:
            print("⚠️ 使用微信窗口中心区域...")
            if self.window_manager.wechat_window_bounds:
                wb = self.window_manager.wechat_window_bounds
                # 使用微信窗口的中心80%区域作为小程序区域
                margin_x = int(wb['width'] * 0.1)
                margin_y = int(wb['height'] * 0.1)
                bounds = {
                    'x': wb['x'] + margin_x,
                    'y': wb['y'] + margin_y + 30,  # 跳过标题栏
                    'width': wb['width'] - 2 * margin_x,
                    'height': wb['height'] - 2 * margin_y - 30
                }
            else:
                print("❌ 微信窗口未初始化，无法截图")
                return None
        
        # 使用检测到的精确边界
        if filename is None:
            filename = CrawlerConfig.get_timestamp_filename("miniprogram")
        
        filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
        
        try:
            # 使用PIL的ImageGrab进行精确截图
            screenshot = ImageGrab.grab(bbox=(
                bounds['x'], 
                bounds['y'], 
                bounds['x'] + bounds['width'], 
                bounds['y'] + bounds['height']
            ))
            
            screenshot.save(filepath)
            print(f"📸 小程序截图已保存: {filename} (区域: {bounds['width']}x{bounds['height']})")
            
            # 进行截图尺寸比对和自我检查
            self.validate_screenshot_result(filepath, bounds)
            
            return filepath
            
        except Exception as e:
            print(f"❌ 截图失败: {e}")
            return None
    
    def validate_screenshot_result(self, screenshot_path, detected_bounds):
        """验证截图结果的正确性"""
        try:
            if not os.path.exists(screenshot_path):
                print(f"❌ 截图文件不存在: {screenshot_path}")
                return False
            
            # 读取截图
            screenshot = Image.open(screenshot_path)
            actual_width, actual_height = screenshot.size
            
            print(f"\n📊 截图结果自我检查:")
            print(f"=" * 50)
            print(f"🎯 检测到的边界: {detected_bounds}")
            print(f"📐 实际截图尺寸: {actual_width} x {actual_height} 像素")
            
            # 检查尺寸一致性
            width_match = actual_width == detected_bounds['width']
            height_match = actual_height == detected_bounds['height']
            
            print(f"✅ 宽度匹配: {width_match} ({actual_width} vs {detected_bounds['width']})")
            print(f"✅ 高度匹配: {height_match} ({actual_height} vs {detected_bounds['height']})")
            
            # 与目标尺寸比较（参考您提供的微信截图）
            # 根据图片，小程序宽度应该在350-450像素之间，高度在500-800像素之间
            target_width_range = (350, 450)
            target_height_range = (500, 800)
            
            width_in_range = target_width_range[0] <= actual_width <= target_width_range[1]
            height_in_range = target_height_range[0] <= actual_height <= target_height_range[1]
            
            print(f"🎯 宽度在目标范围内: {width_in_range} ({target_width_range[0]}-{target_width_range[1]})")
            print(f"🎯 高度在目标范围内: {height_in_range} ({target_height_range[0]}-{target_height_range[1]})")
            
            # 计算与414像素的差距（您之前提到的目标宽度）
            width_diff_414 = abs(actual_width - 414)
            print(f"📏 与414像素的差距: {width_diff_414} 像素")
            
            # 长宽比检查
            aspect_ratio = actual_height / actual_width
            print(f"📐 长宽比: {aspect_ratio:.2f}")
            
            # 综合评估
            score = 0
            if width_match and height_match:
                score += 20
            if width_in_range:
                score += 30
            if height_in_range:
                score += 20
            if width_diff_414 < 50:
                score += 20
            if 1.2 < aspect_ratio < 2.5:
                score += 10
            
            print(f"🏆 综合评分: {score}/100")
            
            if score >= 70:
                print("✅ 截图质量优秀！")
                return True
            elif score >= 50:
                print("⚠️ 截图质量良好，但可能需要优化")
                return True
            else:
                print("❌ 截图质量不佳，建议重新检测")
                return False
                
        except Exception as e:
            print(f"❌ 截图验证失败: {e}")
            return False
    
    def _expand_screenshot_bounds(self, bounds, expansion_x=5, expansion_y=5):
        """轻微扩展截图边界以确保完整覆盖"""
        expanded = {
            'x': max(0, bounds['x'] - expansion_x),
            'y': max(0, bounds['y'] - expansion_y),
            'width': bounds['width'] + 2 * expansion_x,
            'height': bounds['height'] + 2 * expansion_y
        }
        
        # 确保不超出屏幕边界
        screen_width, screen_height = pyautogui.size()
        if expanded['x'] + expanded['width'] > screen_width:
            expanded['width'] = screen_width - expanded['x']
        if expanded['y'] + expanded['height'] > screen_height:
            expanded['height'] = screen_height - expanded['y']
        
        print(f"📐 轻微扩展截图区域: 原始{bounds['width']}x{bounds['height']} -> 扩展{expanded['width']}x{expanded['height']}")
        return expanded
    
    def scroll_in_mini_program(self, direction='down', distance=None):
        """在小程序区域内滚动"""
        bounds = self.window_manager.get_mini_program_bounds()
        if not bounds:
            print("⚠️ 小程序区域未设置，使用默认区域")
            # 使用微信窗口中心进行滚动
            if self.window_manager.wechat_window_bounds:
                scroll_x = self.window_manager.wechat_window_bounds['x'] + self.window_manager.wechat_window_bounds['width'] // 2
                scroll_y = self.window_manager.wechat_window_bounds['y'] + self.window_manager.wechat_window_bounds['height'] // 2
            else:
                return False
        else:
            # 在小程序区域中心滚动
            scroll_x = bounds['x'] + bounds['width'] // 2
            scroll_y = bounds['y'] + bounds['height'] // 2
        
        if distance is None:
            distance = CrawlerConfig.SCROLL_DISTANCE
        
        try:
            scroll_amount = distance if direction == 'down' else -distance
            pyautogui.scroll(-scroll_amount, x=scroll_x, y=scroll_y)
            time.sleep(CrawlerConfig.SCROLL_DELAY)
            print(f"📜 在位置 ({scroll_x}, {scroll_y}) 向{direction}滚动")
            return True
        except Exception as e:
            print(f"❌ 滚动失败: {e}")
            return False
    
    def take_full_page_screenshot(self):
        """滚动截取小程序的完整页面"""
        print("📜 开始滚动截取小程序完整页面...")
        
        # 确保聚焦到小程序
        if not self.window_manager.focus_mini_program_area():
            print("⚠️ 聚焦小程序失败，继续尝试截图")
        
        screenshots = []
        
        # 初始截图
        initial_screenshot = self.take_mini_program_screenshot("scroll_0.png")
        if not initial_screenshot:
            return None, []
        screenshots.append(initial_screenshot)
        
        # 滚动并截图
        for i in range(1, CrawlerConfig.MAX_SCROLLS + 1):
            # 向下滚动
            if not self.scroll_in_mini_program('down'):
                break
            
            # 等待页面稳定
            time.sleep(1)
            
            # 截图
            scroll_screenshot = self.take_mini_program_screenshot(f"scroll_{i}.png")
            if not scroll_screenshot:
                break
            screenshots.append(scroll_screenshot)
            
            # 检查是否到达页面底部
            if i > 2 and self.are_screenshots_similar(screenshots[-1], screenshots[-2]):
                print(f"📄 检测到小程序页面底部，停止滚动 (滚动{i}次)")
                break
        
        # 拼接截图
        full_screenshot_path = self.stitch_screenshots(screenshots)
        if full_screenshot_path:
            print(f"🖼️ 小程序完整页面截图已生成: {os.path.basename(full_screenshot_path)}")
        
        return full_screenshot_path, screenshots
    
    def are_screenshots_similar(self, img1_path, img2_path):
        """比较两张截图的相似度"""
        try:
            img1 = cv2.imread(img1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(img2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                return False
            
            # 确保图片尺寸相同
            if img1.shape != img2.shape:
                # 调整到相同尺寸
                height = min(img1.shape[0], img2.shape[0])
                width = min(img1.shape[1], img2.shape[1])
                img1 = img1[:height, :width]
                img2 = img2[:height, :width]
            
            # 计算结构相似性
            similarity = ssim(img1, img2)
            print(f"🔍 截图相似度: {similarity:.3f}")
            return similarity > CrawlerConfig.SIMILARITY_THRESHOLD
            
        except Exception as e:
            print(f"⚠️ 截图相似度比较失败: {e}")
            return False
    
    def stitch_screenshots(self, screenshot_paths):
        """拼接多张截图为完整页面"""
        if not screenshot_paths:
            return None
            
        try:
            images = []
            for path in screenshot_paths:
                if os.path.exists(path):
                    img = Image.open(path)
                    images.append(img)
                    print(f"📸 加载截图: {os.path.basename(path)} ({img.width}x{img.height})")
            
            if not images:
                return None
            
            # 使用第一张图片的宽度作为标准
            standard_width = images[0].width
            
            # 计算重叠区域（避免重复内容）
            overlap_height = 50  # 假设有50像素的重叠
            
            # 计算总高度（减去重叠部分）
            total_height = images[0].height
            for i in range(1, len(images)):
                total_height += images[i].height - overlap_height
            
            # 创建新图像
            stitched = Image.new('RGB', (standard_width, total_height))
            
            # 拼接图像
            y_offset = 0
            for i, img in enumerate(images):
                if i == 0:
                    # 第一张图片完整粘贴
                    stitched.paste(img, (0, y_offset))
                    y_offset += img.height
                else:
                    # 后续图片跳过重叠部分
                    cropped_img = img.crop((0, overlap_height, img.width, img.height))
                    stitched.paste(cropped_img, (0, y_offset))
                    y_offset += cropped_img.height
            
            # 保存拼接后的图像
            stitched_path = os.path.join(
                CrawlerConfig.SCREENSHOTS_DIR, 
                CrawlerConfig.get_timestamp_filename("full_page")
            )
            stitched.save(stitched_path)
            
            print(f"🖼️ 拼接完成: {standard_width}x{total_height} 像素")
            return stitched_path
            
        except Exception as e:
            print(f"❌ 截图拼接失败: {e}")
            return screenshot_paths[0] if screenshot_paths else None
    
    def take_debug_screenshot(self, filename="debug.png"):
        """拍摄调试截图，显示当前整个屏幕状态"""
        try:
            filepath = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
            screenshot = ImageGrab.grab()
            screenshot.save(filepath)
            print(f"🐛 调试截图已保存: {filename}")
            return filepath
        except Exception as e:
            print(f"❌ 调试截图失败: {e}")
            return None
    
    def clean_old_screenshots(self):
        """清理旧的截图文件"""
        if os.path.exists(CrawlerConfig.SCREENSHOTS_DIR):
            for filename in os.listdir(CrawlerConfig.SCREENSHOTS_DIR):
                if filename.endswith(('.png', '.jpg', '.jpeg')):
                    file_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, filename)
                    try:
                        os.remove(file_path)
                        print(f"🗑️ 已删除旧截图: {filename}")
                    except Exception as e:
                        print(f"⚠️ 删除截图失败: {filename} - {e}")
    
    def compare_screenshot_with_target(self, screenshot_path, target_width=414):
        """比对截图结果与目标尺寸"""
        try:
            if not os.path.exists(screenshot_path):
                print(f"❌ 截图文件不存在: {screenshot_path}")
                return False
            
            # 读取截图
            screenshot = Image.open(screenshot_path)
            actual_width, actual_height = screenshot.size
            
            print(f"📊 截图尺寸比对:")
            print(f"   实际尺寸: {actual_width} x {actual_height} 像素")
            print(f"   目标宽度: {target_width} 像素")
            
            width_diff = abs(actual_width - target_width)
            print(f"   宽度差距: {width_diff} 像素")
            
            # 计算精度
            accuracy = max(0, 100 - (width_diff / target_width * 100))
            print(f"   宽度精度: {accuracy:.1f}%")
            
            # 评估结果
            if width_diff <= 10:
                print("✅ 截图尺寸非常精确！")
                return True
            elif width_diff <= 20:
                print("✅ 截图尺寸较为精确")
                return True
            elif width_diff <= 50:
                print("⚠️ 截图尺寸有一定偏差")
                return False
            else:
                print("❌ 截图尺寸偏差较大")
                return False
                
        except Exception as e:
            print(f"❌ 截图比对失败: {e}")
            return False
    
    def detect_miniprogram_by_edge_detection(self):
        """通过边缘检测直接识别小程序的灰色边框"""
        if not self.window_manager.wechat_window_bounds:
            return None
        
        try:
            # 截取整个微信窗口
            wechat_bounds = self.window_manager.wechat_window_bounds
            full_screenshot = ImageGrab.grab(bbox=(
                wechat_bounds['x'],
                wechat_bounds['y'],
                wechat_bounds['x'] + wechat_bounds['width'],
                wechat_bounds['y'] + wechat_bounds['height']
            ))
            
            # 转换为OpenCV格式
            screenshot_cv = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
            height, width = screenshot_cv.shape[:2]
            
            # 保存原始图像
            debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_edge_detection.png")
            cv2.imwrite(debug_path, screenshot_cv)
            print(f"🐛 边缘检测调试图像已保存: {debug_path}")
            
            # 转换为HSV色彩空间，更好地检测灰色边框
            hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # 检测小程序特有的灰色边框
            # 小程序边框通常是中等灰度值（100-180）
            gray_frame_mask = cv2.inRange(gray, 80, 200)
            
            # 保存灰色检测结果
            gray_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_gray_detection.png")
            cv2.imwrite(gray_debug_path, gray_frame_mask)
            print(f"🐛 灰色检测结果已保存: {gray_debug_path}")
            
            # 使用更精确的边缘检测
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # 保存边缘检测结果
            edge_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_edges_only.png")
            cv2.imwrite(edge_debug_path, edges)
            print(f"🐛 边缘检测结果已保存: {edge_debug_path}")
            
            # 结合灰色检测和边缘检测
            combined_mask = cv2.bitwise_and(gray_frame_mask, edges)
            
            # 形态学操作，连接边框
            kernel = np.ones((3, 3), np.uint8)
            combined_mask = cv2.morphologyEx(combined_mask, cv2.MORPH_CLOSE, kernel)
            combined_mask = cv2.dilate(combined_mask, kernel, iterations=2)
            
            # 保存组合检测结果
            combined_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_combined_detection.png")
            cv2.imwrite(combined_debug_path, combined_mask)
            print(f"🐛 组合检测结果已保存: {combined_debug_path}")
            
            # 查找轮廓
            contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 在原图上绘制检测到的轮廓（用于调试）
            debug_contours = screenshot_cv.copy()
            cv2.drawContours(debug_contours, contours, -1, (0, 255, 0), 2)
            contour_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_contours.png")
            cv2.imwrite(contour_debug_path, debug_contours)
            print(f"🐛 轮廓检测结果已保存: {contour_debug_path}")
            
            # 分析轮廓，寻找小程序灰色边框
            miniprogram_candidates = []
            
            print(f"🔍 检测到 {len(contours)} 个轮廓")
            
            for i, contour in enumerate(contours):
                # 计算轮廓面积
                area = cv2.contourArea(contour)
                if area < 20000:  # 降低面积阈值以查看更多候选区域
                    continue
                
                # 获取轮廓的边界矩形
                x, y, w, h = cv2.boundingRect(contour)
                
                # 基本尺寸检查 - 显示所有检测到的区域
                print(f"🔍 轮廓 {i}: 位置({x},{y}) 尺寸({w}x{h}) 面积({area})")
                
                # 检查区域内的颜色特征
                roi = gray[y:y+h, x:x+w]
                mean_gray = np.mean(roi)
                std_gray = np.std(roi)
                
                print(f"   颜色特征: 平均灰度{mean_gray:.1f}, 标准差{std_gray:.1f}")
                
                # 计算轮廓的近似多边形
                epsilon = 0.02 * cv2.arcLength(contour, True)
                approx = cv2.approxPolyDP(contour, epsilon, True)
                
                # 检查是否符合小程序特征
                if w > 200 and h > 300:  # 降低最小尺寸要求
                    aspect_ratio = h / w
                    
                    # 小程序特征检查 - 放宽条件
                    if (aspect_ratio > 0.8 and  # 降低长宽比要求
                        w < width * 0.95 and h < height * 0.95 and  # 不能占满整个窗口
                        50 < mean_gray < 250):  # 放宽灰度范围
                        
                        # 计算轮廓的紧密度
                        perimeter = cv2.arcLength(contour, True)
                        compactness = (perimeter * perimeter) / area if area > 0 else float('inf')
                        
                        # 计算评分
                        score = 0
                        
                        # 宽度评分（接近414像素）
                        width_diff = abs(w - 414)
                        if width_diff < 30:
                            score += 50
                        elif width_diff < 60:
                            score += 35
                        elif width_diff < 100:
                            score += 20
                        elif width_diff < 150:
                            score += 10
                        
                        # 长宽比评分
                        if 1.2 < aspect_ratio < 2.5:
                            score += 25
                        elif 0.8 < aspect_ratio < 3.0:
                            score += 15
                        
                        # 灰色特征评分
                        if 80 < mean_gray < 180:  # 典型的小程序边框灰度
                            score += 20
                        elif 50 < mean_gray < 220:
                            score += 10
                        
                        # 形状规整度评分
                        if compactness < 30:
                            score += 15
                        elif compactness < 50:
                            score += 8
                        
                        # 面积评分
                        if area > 100000:
                            score += 12
                        elif area > 60000:
                            score += 8
                        elif area > 30000:
                            score += 4
                        
                        # 顶点数量评分（接近矩形）
                        if 4 <= len(approx) <= 10:
                            score += 10
                        elif len(approx) <= 15:
                            score += 5
                        
                        miniprogram_candidates.append({
                            'bounds': (x, y, w, h),
                            'contour': contour,
                            'approx': approx,
                            'score': score,
                            'area': area,
                            'compactness': compactness,
                            'vertices': len(approx),
                            'aspect_ratio': aspect_ratio,
                            'mean_gray': mean_gray,
                            'std_gray': std_gray
                        })
                        
                        print(f"✅ 灰色边框候选区域 {i}: ({x},{y},{w},{h})")
                        print(f"   面积:{area}, 长宽比:{aspect_ratio:.2f}, 平均灰度:{mean_gray:.1f}")
                        print(f"   顶点:{len(approx)}, 评分:{score}")
                    else:
                        print(f"   ❌ 不符合小程序特征: 长宽比{aspect_ratio:.2f} 或灰度{mean_gray:.1f}")
                else:
                    print(f"   ❌ 尺寸太小: {w}x{h}")
            
            # 选择最佳候选区域
            if miniprogram_candidates:
                # 按评分排序
                miniprogram_candidates.sort(key=lambda x: x['score'], reverse=True)
                best_candidate = miniprogram_candidates[0]
                
                print(f"\n📊 找到 {len(miniprogram_candidates)} 个候选区域，最佳评分: {best_candidate['score']}")
                
                # 显示前3个候选区域的详细信息
                for i, candidate in enumerate(miniprogram_candidates[:3]):
                    x, y, w, h = candidate['bounds']
                    print(f"   候选{i+1}: ({x},{y},{w},{h}) 评分:{candidate['score']} 灰度:{candidate['mean_gray']:.1f}")
                
                if best_candidate['score'] > 30:  # 降低评分阈值
                    x, y, w, h = best_candidate['bounds']
                    
                    # 绘制最佳候选区域
                    best_debug = screenshot_cv.copy()
                    cv2.rectangle(best_debug, (x, y), (x + w, y + h), (0, 0, 255), 3)
                    cv2.drawContours(best_debug, [best_candidate['contour']], -1, (255, 0, 0), 2)
                    
                    # 标注信息
                    cv2.putText(best_debug, f"Score: {best_candidate['score']}", 
                               (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(best_debug, f"Size: {w}x{h}", 
                               (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    cv2.putText(best_debug, f"Gray: {best_candidate['mean_gray']:.1f}", 
                               (x, y-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    
                    best_debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, "debug_best_detection.png")
                    cv2.imwrite(best_debug_path, best_debug)
                    print(f"🐛 最佳检测结果已保存: {best_debug_path}")
                    
                    actual_bounds = {
                        'x': wechat_bounds['x'] + x,
                        'y': wechat_bounds['y'] + y,
                        'width': w,
                        'height': h
                    }
                    
                    print(f"🎯 检测到小程序灰色边框区域: {actual_bounds}")
                    print(f"   评分: {best_candidate['score']}")
                    print(f"   面积: {best_candidate['area']}")
                    print(f"   长宽比: {best_candidate['aspect_ratio']:.2f}")
                    print(f"   平均灰度: {best_candidate['mean_gray']:.1f}")
                    print(f"   宽度与目标414像素的差距: {abs(w - 414)} 像素")
                    
                    return actual_bounds
                else:
                    print(f"⚠️ 候选区域评分过低: {best_candidate['score']}")
                    self._show_detection_tips()
                    return None
            else:
                print("⚠️ 未找到合适的小程序灰色边框区域")
                self._show_detection_tips()
                return None
            
        except Exception as e:
            print(f"⚠️ 边缘检测失败: {e}")
            import traceback
            traceback.print_exc()
            self._show_detection_tips()
        
        return None
    
    def _show_detection_tips(self):
        """显示检测失败时的用户提示"""
        print("\n" + "="*60)
        print("🔧 小程序边框检测失败，请检查以下条件：")
        print("="*60)
        print("📋 检测要求：")
        print("   1. 小程序必须完全显示在微信窗口中")
        print("   2. 小程序应该有明显的灰色边框")
        print("   3. 小程序内容区域应该是竖向布局（高度>宽度）")
        print("   4. 小程序宽度应该接近414像素")
        print("   5. 背景不应该是纯白色或与边框颜色相近")
        print("\n💡 建议操作：")
        print("   • 确保小程序完全加载完成")
        print("   • 调整微信窗口大小，确保小程序完整显示")
        print("   • 如果小程序是横向布局，可能需要旋转设备")
        print("   • 检查小程序是否有明显的边框线")
        print("   • 尝试切换到其他小程序页面")
        print("\n🐛 调试信息：")
        print("   • 查看生成的调试图像了解检测过程")
        print("   • debug_edge_detection.png - 原始截图")
        print("   • debug_gray_detection.png - 灰色检测结果")
        print("   • debug_edges_only.png - 边缘检测结果")
        print("   • debug_contours.png - 轮廓检测结果")
        print("="*60) 
    
    def detect_miniprogram_by_system_windows(self):
        """通过系统窗口信息检测小程序区域（类似Snipaste的实现）"""
        try:
            print("🔍 开始系统级窗口检测...")
            
            # 获取所有窗口标题
            all_titles = gw.getAllTitles()
            print(f"📊 检测到 {len(all_titles)} 个窗口标题")
            
            # 查找微信相关窗口
            wechat_titles = []
            for title in all_titles:
                if title and ('微信' in title or 'WeChat' in title or '向僧户小助手' in title):
                    wechat_titles.append(title)
                    print(f"🔍 发现微信相关窗口: '{title}'")
            
            if not wechat_titles:
                print("⚠️ 未找到微信相关窗口")
                return None
            
            # 分析每个微信窗口，寻找小程序内容
            for title in wechat_titles:
                try:
                    # 获取窗口几何信息
                    window_geometry = gw.getWindowGeometry(title)
                    if not window_geometry:
                        print(f"   ❌ 无法获取窗口几何信息: {title}")
                        continue
                    
                    left, top, width, height = window_geometry
                    
                    # 转换为整数坐标
                    left, top, width, height = int(left), int(top), int(width), int(height)
                    
                    if width < 300 or height < 400:
                        print(f"   ❌ 窗口太小，跳过: {width}x{height}")
                        continue
                    
                    print(f"🔍 分析窗口: '{title}' - 位置({left},{top}) 尺寸({width}x{height})")
                    
                    # 截取窗口内容进行分析
                    window_screenshot = ImageGrab.grab(bbox=(left, top, left + width, top + height))
                    
                    # 保存窗口截图用于调试
                    safe_title = title.replace('/', '_').replace(':', '_')
                    debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, f"debug_window_{safe_title}.png")
                    window_screenshot.save(debug_path)
                    print(f"🐛 窗口截图已保存: {debug_path}")
                    
                    # 转换为OpenCV格式分析
                    screenshot_cv = cv2.cvtColor(np.array(window_screenshot), cv2.COLOR_RGB2BGR)
                    
                    # 创建一个模拟窗口对象
                    class MockWindow:
                        def __init__(self, title, left, top, width, height):
                            self.title = title
                            self.left = left
                            self.top = top
                            self.width = width
                            self.height = height
                    
                    mock_window = MockWindow(title, left, top, width, height)
                    
                    # 检测小程序特征区域
                    miniprogram_bounds = self._analyze_window_for_miniprogram(screenshot_cv, mock_window)
                    
                    if miniprogram_bounds:
                        # 转换为全局坐标
                        global_bounds = {
                            'x': left + miniprogram_bounds['x'],
                            'y': top + miniprogram_bounds['y'],
                            'width': miniprogram_bounds['width'],
                            'height': miniprogram_bounds['height']
                        }
                        
                        print(f"🎯 在窗口 '{title}' 中检测到小程序区域:")
                        print(f"   局部坐标: {miniprogram_bounds}")
                        print(f"   全局坐标: {global_bounds}")
                        
                        return global_bounds
                        
                except Exception as e:
                    print(f"⚠️ 分析窗口失败: {e}")
                    continue
            
            print("⚠️ 在所有微信窗口中都未找到小程序区域")
            return None
            
        except Exception as e:
            print(f"⚠️ 系统窗口检测失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _analyze_window_for_miniprogram(self, screenshot_cv, window):
        """分析窗口内容，寻找小程序区域"""
        height, width = screenshot_cv.shape[:2]
        gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        print(f"   📐 窗口内容尺寸: {width}x{height}")
        
        # 特殊情况：如果窗口尺寸本身就符合小程序特征，直接使用整个窗口
        aspect_ratio = height / width
        if (350 <= width <= 500 and 500 <= height <= 900 and 1.2 <= aspect_ratio <= 2.5):
            print(f"   🎯 窗口尺寸符合小程序特征，直接使用整个窗口")
            print(f"   📏 宽度: {width}, 高度: {height}, 长宽比: {aspect_ratio:.2f}")
            
            # 验证这确实是小程序内容
            # 检查是否有典型的小程序UI元素
            has_content = self._verify_miniprogram_content(screenshot_cv)
            
            if has_content:
                return {
                    'x': 0,
                    'y': 0,
                    'width': width,
                    'height': height
                }
            else:
                print(f"   ⚠️ 窗口尺寸符合但内容验证失败")
        
        # 方法1: 检测小程序的典型UI特征
        # 小程序通常有标题栏、内容区域、底部区域的三段式布局
        
        # 检测水平分割线（标题栏下方、内容区域等）
        horizontal_edges = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        horizontal_edges = np.abs(horizontal_edges)
        
        # 计算每行的边缘强度
        row_edge_strength = np.mean(horizontal_edges, axis=1)
        
        # 寻找强边缘（可能是分割线）
        strong_edges = np.where(row_edge_strength > np.mean(row_edge_strength) + 2 * np.std(row_edge_strength))[0]
        
        if len(strong_edges) > 0:
            print(f"   🔍 检测到 {len(strong_edges)} 个水平分割线")
        
        # 方法2: 检测小程序的边框
        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 分析轮廓，寻找小程序边框
        candidates = []
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 30000:  # 降低面积阈值
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / w
            
            # 检查是否符合小程序特征
            if (w > 200 and h > 300 and  # 降低最小尺寸要求
                aspect_ratio > 0.6 and  # 支持横向和竖向
                w < width * 0.95 and h < height * 0.95):  # 不能占满整个窗口
                
                # 计算评分
                score = 0
                
                # 尺寸评分
                if 350 < w < 500:  # 接近小程序典型宽度
                    score += 30
                elif 300 < w < 600:
                    score += 20
                elif 200 < w < 700:
                    score += 10
                
                # 长宽比评分
                if 1.2 < aspect_ratio < 2.5:  # 竖向小程序
                    score += 25
                elif 0.6 < aspect_ratio < 1.2:  # 横向小程序
                    score += 20
                elif 0.5 < aspect_ratio < 3.0:
                    score += 10
                
                # 位置评分（居中的区域得分更高）
                center_x = x + w // 2
                center_y = y + h // 2
                if width * 0.2 < center_x < width * 0.8:
                    score += 15
                if height * 0.1 < center_y < height * 0.9:
                    score += 10
                
                # 面积评分
                if area > 100000:
                    score += 15
                elif area > 60000:
                    score += 10
                elif area > 30000:
                    score += 5
                
                candidates.append({
                    'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                    'score': score,
                    'area': area,
                    'aspect_ratio': aspect_ratio
                })
                
                print(f"   ✅ 候选区域 {i}: ({x},{y},{w},{h}) 评分:{score} 长宽比:{aspect_ratio:.2f}")
        
        # 方法3: 基于颜色分析的内容区域检测
        # 检测小程序的典型颜色模式
        hsv = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2HSV)
        
        # 检测内容区域（非纯色背景）
        # 计算颜色方差
        color_variance = np.var(screenshot_cv, axis=2)
        content_mask = color_variance > 50  # 降低阈值
        
        # 寻找内容密集区域
        kernel = np.ones((10, 10), np.uint8)
        content_mask_dilated = cv2.dilate(content_mask.astype(np.uint8), kernel, iterations=2)
        
        # 查找内容区域的轮廓
        content_contours, _ = cv2.findContours(content_mask_dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in content_contours:
            area = cv2.contourArea(contour)
            if area < 50000:  # 降低面积要求
                continue
            
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = h / w
            
            if (w > 200 and h > 250 and
                w < width * 0.95 and h < height * 0.95):
                
                score = 0
                
                # 尺寸评分
                if 350 < w < 500:
                    score += 25
                elif 300 < w < 600:
                    score += 15
                elif 200 < w < 700:
                    score += 8
                
                # 长宽比评分
                if 1.0 < aspect_ratio < 2.5:
                    score += 20
                elif 0.7 < aspect_ratio < 3.0:
                    score += 10
                
                # 内容密度评分
                roi_variance = np.mean(color_variance[y:y+h, x:x+w])
                if roi_variance > 150:
                    score += 20
                elif roi_variance > 75:
                    score += 10
                elif roi_variance > 50:
                    score += 5
                
                candidates.append({
                    'bounds': {'x': x, 'y': y, 'width': w, 'height': h},
                    'score': score,
                    'area': area,
                    'aspect_ratio': aspect_ratio,
                    'method': 'content_analysis'
                })
                
                print(f"   ✅ 内容分析候选区域: ({x},{y},{w},{h}) 评分:{score} 内容密度:{roi_variance:.1f}")
        
        # 选择最佳候选区域
        if candidates:
            # 按评分排序
            candidates.sort(key=lambda x: x['score'], reverse=True)
            best_candidate = candidates[0]
            
            print(f"   📊 找到 {len(candidates)} 个候选区域，最佳评分: {best_candidate['score']}")
            
            if best_candidate['score'] > 20:  # 降低评分阈值
                # 绘制检测结果用于调试
                debug_img = screenshot_cv.copy()
                bounds = best_candidate['bounds']
                cv2.rectangle(debug_img, 
                            (bounds['x'], bounds['y']), 
                            (bounds['x'] + bounds['width'], bounds['y'] + bounds['height']), 
                            (0, 0, 255), 3)
                
                cv2.putText(debug_img, f"Score: {best_candidate['score']}", 
                           (bounds['x'], bounds['y']-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                safe_title = window.title.replace('/', '_').replace(':', '_')
                debug_path = os.path.join(CrawlerConfig.SCREENSHOTS_DIR, f"debug_detection_{safe_title}.png")
                cv2.imwrite(debug_path, debug_img)
                print(f"   🐛 检测结果已保存: {debug_path}")
                
                return best_candidate['bounds']
            else:
                print(f"   ⚠️ 最佳候选区域评分过低: {best_candidate['score']}")
        else:
            print("   ⚠️ 未找到合适的候选区域")
        
        return None
    
    def _verify_miniprogram_content(self, screenshot_cv):
        """验证是否为小程序内容"""
        try:
            height, width = screenshot_cv.shape[:2]
            gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
            
            # 检查1: 内容复杂度
            # 小程序应该有一定的内容复杂度
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (width * height)
            
            # 检查2: 颜色多样性
            # 小程序通常有多种颜色
            color_variance = np.var(screenshot_cv, axis=2)
            avg_variance = np.mean(color_variance)
            
            # 检查3: 文字区域
            # 小程序通常包含文字
            text_regions = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))
            text_density = np.sum(text_regions > 0) / (width * height)
            
            print(f"   🔍 内容验证: 边缘密度{edge_density:.3f}, 颜色方差{avg_variance:.1f}, 文字密度{text_density:.3f}")
            
            # 综合判断
            if edge_density > 0.02 and avg_variance > 100 and text_density > 0.01:
                print(f"   ✅ 内容验证通过")
                return True
            else:
                print(f"   ❌ 内容验证失败")
                return False
                
        except Exception as e:
            print(f"   ⚠️ 内容验证异常: {e}")
            return False 