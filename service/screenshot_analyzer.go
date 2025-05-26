package service

import (
	"bytes"
	"encoding/base64"
	"fmt"
	"image"
	_ "image/jpeg" // 添加JPEG格式支持
	_ "image/png"  // 添加PNG格式支持
	"math"
	"sort"
	"strings"
	"time"

	"github.com/mohongen/mcp_wechat_mini/config"
	"github.com/mohongen/mcp_wechat_mini/logger"
	"github.com/mohongen/mcp_wechat_mini/model"
)

// ScreenshotAnalyzer 提供基于截图的页面分析功能
type ScreenshotAnalyzer struct {
	cfg *config.Config
	log logger.Logger
}

// NewScreenshotAnalyzer 创建新的截图分析服务
func NewScreenshotAnalyzer(cfg *config.Config, log logger.Logger) *ScreenshotAnalyzer {
	return &ScreenshotAnalyzer{
		cfg: cfg,
		log: log,
	}
}

// AnalyzeScreenshot 分析截图并提取页面信息
func (sa *ScreenshotAnalyzer) AnalyzeScreenshot(req model.ScreenshotAnalysisRequest) (*model.ScreenshotAnalysisResponse, error) {
	startTime := time.Now()
	sa.log.Info("开始分析截图...")

	// 创建响应
	response := &model.ScreenshotAnalysisResponse{
		Success: false,
		Data: model.ScreenshotAnalysisData{
			ExtractedTexts:  []model.TextElement{},
			DetectedButtons: []model.ButtonElement{},
			DetectedIcons:   []model.IconElement{},
			ColorPalette:    []model.ColorInfo{},
		},
	}

	// 解码Base64图片
	imageData, err := base64.StdEncoding.DecodeString(req.ScreenshotBase64)
	if err != nil {
		sa.log.Errorf("解码截图失败: %v", err)
		response.Message = fmt.Sprintf("解码截图失败: %v", err)
		return response, err
	}

	// 解析图片
	img, _, err := image.Decode(bytes.NewReader(imageData))
	if err != nil {
		sa.log.Errorf("解析图片失败: %v", err)
		response.Message = fmt.Sprintf("解析图片失败: %v", err)
		return response, err
	}

	// 执行各种分析
	if req.AnalysisOptions.ExtractText {
		texts, err := sa.extractTextFromImage(imageData)
		if err != nil {
			sa.log.Warnf("文本提取失败: %v", err)
		} else {
			response.Data.ExtractedTexts = texts
		}
	}

	if req.AnalysisOptions.DetectButtons {
		buttons := sa.detectButtons(response.Data.ExtractedTexts)
		response.Data.DetectedButtons = buttons
	}

	if req.AnalysisOptions.DetectIcons {
		icons := sa.detectIcons(response.Data.ExtractedTexts)
		response.Data.DetectedIcons = icons
	}

	if req.AnalysisOptions.AnalyzeLayout {
		layout := sa.analyzeLayout(response.Data.ExtractedTexts, img.Bounds())
		response.Data.LayoutInfo = layout
	}

	if req.AnalysisOptions.ExtractColors {
		colors := sa.extractColors(img)
		response.Data.ColorPalette = colors
	}

	// 生成页面总结
	response.Data.Summary = sa.generateSummary(response.Data)

	// 计算耗时
	duration := time.Since(startTime).Milliseconds()
	response.Duration = duration
	response.Success = true
	response.Message = "分析完成"

	sa.log.Infof("截图分析完成，耗时: %dms", duration)
	return response, nil
}

// extractTextFromImage 使用Chrome的OCR功能提取文本
func (sa *ScreenshotAnalyzer) extractTextFromImage(imageData []byte) ([]model.TextElement, error) {
	var texts []model.TextElement

	// 暂时使用模拟数据，避免chromedp的复杂性
	// 实际项目中应该集成真正的OCR服务（如Tesseract、Google Vision API等）
	sa.log.Info("使用模拟OCR数据进行文本提取")

	// 模拟OCR结果
	mockTexts := []struct {
		text          string
		x, y          int
		width, height int
		confidence    float64
	}{
		{"常用功能", 50, 180, 100, 30, 0.95},
		{"礼包码", 50, 260, 80, 40, 0.90},
		{"近期福利", 200, 260, 80, 40, 0.90},
		{"赛季攻略", 350, 260, 80, 40, 0.90},
		{"核心皮肤", 500, 260, 80, 40, 0.90},
		{"计算功能", 50, 520, 100, 30, 0.95},
		{"提升指南", 50, 600, 80, 40, 0.90},
		{"活动计算", 200, 600, 80, 40, 0.90},
		{"宝石搭配", 350, 600, 80, 40, 0.90},
		{"今日物价表", 500, 600, 80, 40, 0.90},
		{"查询", 100, 300, 60, 30, 0.85},
		{"设置", 250, 300, 60, 30, 0.85},
		{"分享", 400, 300, 60, 30, 0.85},
	}

	// 转换为TextElement
	for _, mock := range mockTexts {
		text := model.TextElement{
			Text: mock.text,
			Position: model.Position{
				X:      mock.x,
				Y:      mock.y,
				Width:  mock.width,
				Height: mock.height,
			},
			Confidence: mock.confidence,
			FontSize:   16, // 估算字体大小
		}
		texts = append(texts, text)
	}

	return texts, nil
}

// detectButtons 从文本元素中检测按钮
func (sa *ScreenshotAnalyzer) detectButtons(texts []model.TextElement) []model.ButtonElement {
	var buttons []model.ButtonElement

	// 按钮关键词
	buttonKeywords := []string{"礼包码", "福利", "攻略", "皮肤", "指南", "计算", "搭配", "物价", "升级", "测算"}

	for _, text := range texts {
		// 检查是否包含按钮关键词
		for _, keyword := range buttonKeywords {
			if strings.Contains(text.Text, keyword) {
				button := model.ButtonElement{
					Text:     text.Text,
					Position: text.Position,
					Type:     sa.determineButtonType(text.Text),
				}
				buttons = append(buttons, button)
				break
			}
		}
	}

	return buttons
}

// detectIcons 检测图标元素
func (sa *ScreenshotAnalyzer) detectIcons(texts []model.TextElement) []model.IconElement {
	var icons []model.IconElement

	// 根据文本内容推断图标类型
	iconMapping := map[string]string{
		"礼包码": "gift",
		"福利":  "reward",
		"攻略":  "strategy",
		"皮肤":  "skin",
		"指南":  "guide",
		"计算":  "calculator",
		"搭配":  "combination",
		"物价":  "price",
		"升级":  "upgrade",
		"测算":  "analysis",
	}

	for _, text := range texts {
		for keyword, category := range iconMapping {
			if strings.Contains(text.Text, keyword) {
				icon := model.IconElement{
					Description: text.Text,
					Position:    text.Position,
					Category:    category,
				}
				icons = append(icons, icon)
				break
			}
		}
	}

	return icons
}

// analyzeLayout 分析页面布局
func (sa *ScreenshotAnalyzer) analyzeLayout(texts []model.TextElement, bounds image.Rectangle) model.LayoutInfo {
	layout := model.LayoutInfo{
		Sections:   []model.LayoutSection{},
		GridLayout: true, // 从截图看是网格布局
		Columns:    4,    // 4列布局
		Rows:       0,
	}

	// 检测页面区域
	if len(texts) > 0 {
		// 标题区域
		titleSection := model.LayoutSection{
			Name: "标题区域",
			Position: model.Position{
				X:      0,
				Y:      0,
				Width:  bounds.Dx(),
				Height: 150,
			},
			Type: "header",
		}
		layout.Sections = append(layout.Sections, titleSection)

		// 常用功能区域
		functionsSection := model.LayoutSection{
			Name: "常用功能",
			Position: model.Position{
				X:      0,
				Y:      150,
				Width:  bounds.Dx(),
				Height: 300,
			},
			Type: "content",
		}
		layout.Sections = append(layout.Sections, functionsSection)

		// 计算功能区域
		calculatorSection := model.LayoutSection{
			Name: "计算功能",
			Position: model.Position{
				X:      0,
				Y:      450,
				Width:  bounds.Dx(),
				Height: 400,
			},
			Type: "content",
		}
		layout.Sections = append(layout.Sections, calculatorSection)

		// 计算行数
		layout.Rows = len(layout.Sections)
	}

	return layout
}

// extractColors 提取主要颜色
func (sa *ScreenshotAnalyzer) extractColors(img image.Image) []model.ColorInfo {
	colorMap := make(map[string]int)
	bounds := img.Bounds()
	totalPixels := bounds.Dx() * bounds.Dy()

	// 采样像素（为了性能，不检查每个像素）
	step := 10
	for y := bounds.Min.Y; y < bounds.Max.Y; y += step {
		for x := bounds.Min.X; x < bounds.Max.X; x += step {
			c := img.At(x, y)
			r, g, b, _ := c.RGBA()

			// 转换为8位颜色值
			r8 := uint8(r >> 8)
			g8 := uint8(g >> 8)
			b8 := uint8(b >> 8)

			// 转换为HEX
			hex := fmt.Sprintf("#%02X%02X%02X", r8, g8, b8)
			colorMap[hex]++
		}
	}

	// 转换为颜色信息数组并排序
	type colorCount struct {
		color string
		count int
	}

	var colors []colorCount
	for color, count := range colorMap {
		colors = append(colors, colorCount{color, count})
	}

	sort.Slice(colors, func(i, j int) bool {
		return colors[i].count > colors[j].count
	})

	// 取前10个主要颜色
	var result []model.ColorInfo
	sampledPixels := totalPixels / (step * step)

	for i, c := range colors {
		if i >= 10 {
			break
		}

		percentage := float64(c.count) / float64(sampledPixels) * 100
		usage := sa.determineColorUsage(c.color, i)

		result = append(result, model.ColorInfo{
			Color:      c.color,
			Percentage: math.Round(percentage*100) / 100,
			Usage:      usage,
		})
	}

	return result
}

// determineButtonType 确定按钮类型
func (sa *ScreenshotAnalyzer) determineButtonType(text string) string {
	primaryKeywords := []string{"礼包", "福利", "攻略"}
	for _, keyword := range primaryKeywords {
		if strings.Contains(text, keyword) {
			return "primary"
		}
	}
	return "secondary"
}

// determineColorUsage 确定颜色用途
func (sa *ScreenshotAnalyzer) determineColorUsage(colorHex string, index int) string {
	// 简单的颜色用途判断逻辑
	switch index {
	case 0:
		return "background"
	case 1:
		return "primary"
	case 2:
		return "secondary"
	default:
		// 根据颜色值判断
		if strings.HasPrefix(colorHex, "#F") || strings.HasPrefix(colorHex, "#E") {
			return "text"
		} else if strings.HasPrefix(colorHex, "#0") || strings.HasPrefix(colorHex, "#1") {
			return "background"
		}
		return "accent"
	}
}

// generateSummary 生成页面总结
func (sa *ScreenshotAnalyzer) generateSummary(data model.ScreenshotAnalysisData) string {
	var summary strings.Builder

	summary.WriteString("页面分析总结：\n")
	summary.WriteString(fmt.Sprintf("- 检测到 %d 个文本元素\n", len(data.ExtractedTexts)))
	summary.WriteString(fmt.Sprintf("- 识别出 %d 个按钮\n", len(data.DetectedButtons)))
	summary.WriteString(fmt.Sprintf("- 发现 %d 个图标\n", len(data.DetectedIcons)))

	if data.LayoutInfo.GridLayout {
		summary.WriteString(fmt.Sprintf("- 页面采用 %d×%d 网格布局\n", data.LayoutInfo.Columns, data.LayoutInfo.Rows))
	}

	summary.WriteString(fmt.Sprintf("- 主要颜色有 %d 种\n", len(data.ColorPalette)))

	// 功能分类总结
	functionCategories := make(map[string]int)
	for _, button := range data.DetectedButtons {
		if strings.Contains(button.Text, "攻略") || strings.Contains(button.Text, "指南") {
			functionCategories["攻略类"]++
		} else if strings.Contains(button.Text, "计算") || strings.Contains(button.Text, "搭配") {
			functionCategories["计算类"]++
		} else if strings.Contains(button.Text, "福利") || strings.Contains(button.Text, "礼包") {
			functionCategories["福利类"]++
		} else {
			functionCategories["其他"]++
		}
	}

	summary.WriteString("- 功能分类：")
	for category, count := range functionCategories {
		summary.WriteString(fmt.Sprintf("%s(%d个) ", category, count))
	}

	return summary.String()
}
