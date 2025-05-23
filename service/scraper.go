package service

import (
	"context"
	"encoding/base64"
	"errors"
	"fmt"
	"time"

	"github.com/chromedp/chromedp"
	"github.com/mohongen/mcp_wechat_mini/config"
	"github.com/mohongen/mcp_wechat_mini/logger"
	"github.com/mohongen/mcp_wechat_mini/model"
)

// Scraper 提供微信小程序页面抓取功能
type Scraper struct {
	cfg *config.Config
	log logger.Logger
}

// NewScraper 创建新的抓取服务
func NewScraper(cfg *config.Config, log logger.Logger) *Scraper {
	return &Scraper{
		cfg: cfg,
		log: log,
	}
}

// ScrapPage 抓取指定的微信小程序页面
func (s *Scraper) ScrapPage(req model.ScrapRequest) (*model.ScrapResponse, error) {
	startTime := time.Now()
	s.log.Infof("开始抓取小程序页面: appID=%s, path=%s", req.AppID, req.PagePath)

	// 创建响应
	response := &model.ScrapResponse{
		Success: false,
		Data: model.MiniProgramPage{
			AppID:     req.AppID,
			PagePath:  req.PagePath,
			CreatedAt: time.Now(),
			UpdatedAt: time.Now(),
		},
	}

	// 创建Chrome实例的配置
	opts := []chromedp.ExecAllocatorOption{
		chromedp.Flag("headless", true),                 // 无头模式
		chromedp.Flag("disable-gpu", true),              // 禁用GPU加速
		chromedp.Flag("no-sandbox", true),               // 禁用沙箱
		chromedp.Flag("disable-dev-shm-usage", true),    // 禁用/dev/shm使用
		chromedp.Flag("disable-setuid-sandbox", true),   // 禁用setuid沙箱
		chromedp.Flag("ignore-certificate-errors", true), // 忽略证书错误
		chromedp.UserAgent(s.cfg.Scraper.UserAgent),     // 设置User-Agent
	}

	// 设置超时上下文
	maxWaitTime := time.Duration(req.Options.MaxWaitTime) * time.Second
	if maxWaitTime == 0 {
		maxWaitTime = s.cfg.Scraper.Timeout
	}

	// 创建Chrome的分配器和上下文
	allocCtx, cancel := chromedp.NewExecAllocator(context.Background(), opts...)
	defer cancel()

	// 创建新的Chrome实例和上下文
	ctx, cancel := chromedp.NewContext(allocCtx)
	defer cancel()

	// 设置超时
	ctx, cancel = context.WithTimeout(ctx, maxWaitTime)
	defer cancel()

	// 构建要访问的小程序页面URL
	// 注意：实际项目中，你需要根据实际情况修改这个URL，这里只是示例
	url := fmt.Sprintf("https://mp.weixin.qq.com/wxamp/%s?appid=%s", req.PagePath, req.AppID)
	for key, value := range req.Params {
		url += fmt.Sprintf("&%s=%s", key, value)
	}

	// 等待小程序加载完成的选择器
	// 注意：这个选择器需要根据实际小程序的DOM结构调整
	loadedSelector := "body"

	// 抓取操作
	var pageTitle, pageContent string
	var screenshot []byte

	tasks := []chromedp.Action{
		chromedp.Navigate(url),                     // 导航到URL
		chromedp.WaitVisible(loadedSelector, chromedp.ByQuery), // 等待页面加载完成
		chromedp.Title(&pageTitle),                 // 获取页面标题
		chromedp.OuterHTML("html", &pageContent),   // 获取整个页面的HTML
	}

	// 如果需要截图
	if req.Options.ScreenshotEnabled {
		tasks = append(tasks, chromedp.CaptureScreenshot(&screenshot))
	}

	// 执行抓取任务
	err := chromedp.Run(ctx, tasks...)
	if err != nil {
		s.log.Errorf("抓取页面失败: %v", err)
		response.Message = fmt.Sprintf("抓取失败: %v", err)
		return response, errors.New("抓取页面失败")
	}

	// 填充抓取结果
	response.Success = true
	response.Message = "抓取成功"
	response.Data.Title = pageTitle
	response.Data.Content = pageContent

	// 如果有截图，转换为Base64
	if screenshot != nil {
		response.Data.Screenshot = base64.StdEncoding.EncodeToString(screenshot)
	}

	// 如果需要获取元数据
	if req.Options.MetadataEnabled {
		metadata, err := s.extractMetadata(ctx, req)
		if err != nil {
			s.log.Warnf("提取元数据失败: %v", err)
		} else {
			response.Data.Metadata = metadata
		}
	}

	// 计算耗时
	duration := time.Since(startTime).Milliseconds()
	response.Duration = duration
	s.log.Infof("完成抓取，耗时: %dms", duration)

	return response, nil
}

// extractMetadata 从页面中提取元数据
func (s *Scraper) extractMetadata(ctx context.Context, req model.ScrapRequest) (model.PageMetadata, error) {
	metadata := model.PageMetadata{
		Components: []model.ComponentInfo{},
		APIs:       []model.APIInfo{},
		Resources:  []model.ResourceInfo{},
	}

	// 这里编写元数据提取逻辑
	// 例如：提取页面中使用的组件、API调用、资源等信息
	// 以下是示例代码，实际应用中需要根据微信小程序的具体结构进行调整

	// 提取组件信息（简单示例）
	var components []struct {
		Name  string `json:"name"`
		Count int    `json:"count"`
	}

	// 使用JavaScript执行DOM查询，找出页面中的组件
	// 注：此处代码仅为示例，需要根据实际小程序结构调整
	err := chromedp.Run(ctx, chromedp.Evaluate(`
		(() => {
			// 这里编写JavaScript脚本来识别和统计页面中的组件
			// 示例：可以通过分析DOM结构、CSS类名等方式识别组件
			const components = [];
			// 假设组件都有特定的前缀"wx-"
			const wxElements = document.querySelectorAll('[class^="wx-"]');
			
			// 统计组件
			const componentMap = new Map();
			for (const el of wxElements) {
				const className = el.className;
				const componentName = className.split(' ').find(c => c.startsWith('wx-'));
				if (componentName) {
					if (componentMap.has(componentName)) {
						componentMap.set(componentName, componentMap.get(componentName) + 1);
					} else {
						componentMap.set(componentName, 1);
					}
				}
			}
			
			// 转换为数组
			for (const [name, count] of componentMap.entries()) {
				components.push({ name, count });
			}
			
			return components;
		})()
	`, &components))

	if err != nil {
		return metadata, fmt.Errorf("提取组件信息失败: %v", err)
	}

	// 转换为我们的模型格式
	for _, comp := range components {
		metadata.Components = append(metadata.Components, model.ComponentInfo{
			Name:  comp.Name,
			Count: comp.Count,
		})
	}

	// 提取资源信息
	var resources []struct {
		Type string `json:"type"`
		URL  string `json:"url"`
	}

	err = chromedp.Run(ctx, chromedp.Evaluate(`
		(() => {
			// 收集页面上的图片资源
			const images = Array.from(document.querySelectorAll('img'))
				.map(img => ({ type: 'image', url: img.src }))
				.filter(img => img.url);
				
			// 收集页面上的视频资源
			const videos = Array.from(document.querySelectorAll('video'))
				.map(video => ({ type: 'video', url: video.src }))
				.filter(video => video.url);
				
			// 合并所有资源
			return [...images, ...videos];
		})()
	`, &resources))

	if err != nil {
		return metadata, fmt.Errorf("提取资源信息失败: %v", err)
	}

	// 转换为我们的模型格式
	for _, res := range resources {
		metadata.Resources = append(metadata.Resources, model.ResourceInfo{
			Type: res.Type,
			URL:  res.URL,
		})
	}

	return metadata, nil
} 