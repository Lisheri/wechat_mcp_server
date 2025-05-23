package server

import (
	"context"
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/mohongen/mcp_wechat_mini/config"
	"github.com/mohongen/mcp_wechat_mini/controller"
	"github.com/mohongen/mcp_wechat_mini/logger"
)

// Server 是HTTP服务器
type Server struct {
	router *gin.Engine
	server *http.Server
	cfg    *config.Config
	log    logger.Logger
}

// New 创建新的HTTP服务器
func New(cfg *config.Config, ctrl *controller.Controller, log logger.Logger) *Server {
	// 设置Gin模式
	gin.SetMode(gin.ReleaseMode)

	// 创建Gin路由器
	router := gin.New()

	// 使用中间件
	router.Use(gin.Recovery()) // 从任何panic恢复
	router.Use(loggerMiddleware(log)) // 日志中间件
	router.Use(corsMiddleware()) // CORS中间件

	// 注册路由
	ctrl.RegisterRoutes(router)

	// 创建HTTP服务器
	srv := &http.Server{
		Addr:         cfg.Server.Address,
		Handler:      router,
		ReadTimeout:  cfg.Server.ReadTimeout,
		WriteTimeout: cfg.Server.WriteTimeout,
	}

	return &Server{
		router: router,
		server: srv,
		cfg:    cfg,
		log:    log,
	}
}

// Start 启动HTTP服务器
func (s *Server) Start() error {
	s.log.Infof("HTTP服务器开始监听: %s", s.cfg.Server.Address)
	return s.server.ListenAndServe()
}

// Stop 优雅地关闭HTTP服务器
func (s *Server) Stop() error {
	// 创建带超时的上下文
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	s.log.Info("正在优雅关闭HTTP服务器...")
	return s.server.Shutdown(ctx)
}

// loggerMiddleware 创建一个日志中间件
func loggerMiddleware(log logger.Logger) gin.HandlerFunc {
	return func(c *gin.Context) {
		// 开始时间
		start := time.Now()
		path := c.Request.URL.Path
		method := c.Request.Method

		// 处理请求
		c.Next()

		// 请求处理完成后
		end := time.Now()
		latency := end.Sub(start)
		statusCode := c.Writer.Status()
		clientIP := c.ClientIP()

		// 记录请求日志
		log.Infof("%s | %d | %s | %s | %s | %v",
			method,
			statusCode,
			clientIP,
			path,
			c.Request.UserAgent(),
			latency,
		)
	}
}

// corsMiddleware 创建一个CORS中间件
func corsMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Writer.Header().Set("Access-Control-Allow-Origin", "*")
		c.Writer.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
		c.Writer.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
} 