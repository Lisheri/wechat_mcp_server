package controller

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/mohongen/mcp_wechat_mini/config"
	"github.com/mohongen/mcp_wechat_mini/logger"
	"github.com/mohongen/mcp_wechat_mini/model"
	"github.com/mohongen/mcp_wechat_mini/service"
)

// Controller 处理HTTP请求的控制器
type Controller struct {
	log               logger.Logger
	cfg               *config.Config
	scraper           *service.Scraper
	screenshotAnalyzer *service.ScreenshotAnalyzer
}

// New 创建新的控制器
func New(log logger.Logger, cfg *config.Config) *Controller {
	return &Controller{
		log:               log,
		cfg:               cfg,
		scraper:           service.NewScraper(cfg, log),
		screenshotAnalyzer: service.NewScreenshotAnalyzer(cfg, log),
	}
}

// RegisterRoutes 注册所有HTTP路由
func (c *Controller) RegisterRoutes(router *gin.Engine) {
	// 健康检查路由
	router.GET("/health", c.health)
	
	// API路由组
	api := router.Group("/api/v1")
	{
		// 微信小程序相关路由
		wxMini := api.Group("/wechat-mini")
		{
			wxMini.POST("/scrap", c.scrapPage)
			wxMini.GET("/history", c.getHistory)
			wxMini.GET("/page/:id", c.getPageById)
			
			// 新增截图分析接口
			wxMini.POST("/analyze-screenshot", c.analyzeScreenshot)
		}
	}
}

// 健康检查接口
func (c *Controller) health(ctx *gin.Context) {
	ctx.JSON(http.StatusOK, gin.H{
		"status": "ok",
		"version": "1.0.0",
	})
}

// 抓取小程序页面
func (c *Controller) scrapPage(ctx *gin.Context) {
	c.log.Info("收到抓取页面请求")
	
	// 解析请求参数
	var req model.ScrapRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		c.log.Errorf("解析请求参数失败: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"message": "请求参数格式错误",
			"error":   err.Error(),
		})
		return
	}
	
	// 参数校验
	if req.AppID == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"message": "AppID不能为空",
		})
		return
	}
	
	if req.PagePath == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"message": "页面路径不能为空",
		})
		return
	}
	
	// 设置默认值
	if req.Options.MaxWaitTime <= 0 {
		req.Options.MaxWaitTime = 30 // 默认30秒
	}
	
	// 调用服务进行抓取
	response, err := c.scraper.ScrapPage(req)
	if err != nil {
		c.log.Errorf("抓取失败: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"message": "抓取过程中发生错误",
			"error":   err.Error(),
		})
		return
	}
	
	// 返回结果
	ctx.JSON(http.StatusOK, response)
}

// 分析截图接口
func (c *Controller) analyzeScreenshot(ctx *gin.Context) {
	c.log.Info("收到截图分析请求")
	
	// 解析请求参数
	var req model.ScreenshotAnalysisRequest
	if err := ctx.ShouldBindJSON(&req); err != nil {
		c.log.Errorf("解析请求参数失败: %v", err)
		ctx.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"message": "请求参数格式错误",
			"error":   err.Error(),
		})
		return
	}
	
	// 参数校验
	if req.ScreenshotBase64 == "" {
		ctx.JSON(http.StatusBadRequest, gin.H{
			"success": false,
			"message": "截图数据不能为空",
		})
		return
	}
	
	// 设置默认分析选项
	if !req.AnalysisOptions.ExtractText && 
	   !req.AnalysisOptions.DetectButtons && 
	   !req.AnalysisOptions.DetectIcons && 
	   !req.AnalysisOptions.AnalyzeLayout && 
	   !req.AnalysisOptions.ExtractColors {
		// 如果没有指定任何选项，则启用所有分析
		req.AnalysisOptions = model.ScreenshotAnalysisOptions{
			ExtractText:   true,
			DetectButtons: true,
			DetectIcons:   true,
			AnalyzeLayout: true,
			ExtractColors: true,
		}
	}
	
	// 调用服务进行分析
	response, err := c.screenshotAnalyzer.AnalyzeScreenshot(req)
	if err != nil {
		c.log.Errorf("截图分析失败: %v", err)
		ctx.JSON(http.StatusInternalServerError, gin.H{
			"success": false,
			"message": "分析过程中发生错误",
			"error":   err.Error(),
		})
		return
	}
	
	// 返回结果
	ctx.JSON(http.StatusOK, response)
}

// 获取历史抓取记录
func (c *Controller) getHistory(ctx *gin.Context) {
	// 注意：这里需要实现数据库查询逻辑
	// 由于示例中未包含数据库实现，这里只返回一个空结果
	ctx.JSON(http.StatusOK, gin.H{
		"success": true,
		"message": "查询成功",
		"data": []interface{}{},
		"total": 0,
	})
}

// 根据ID获取页面详情
func (c *Controller) getPageById(ctx *gin.Context) {
	id := ctx.Param("id")
	
	// 注意：这里需要实现数据库查询逻辑
	// 由于示例中未包含数据库实现，这里只返回一个错误
	ctx.JSON(http.StatusNotFound, gin.H{
		"success": false,
		"message": "未找到指定ID的页面记录",
		"id": id,
	})
} 