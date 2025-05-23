package main

import (
	"flag"
	"os"
	"os/signal"
	"syscall"

	"github.com/mohongen/mcp_wechat_mini/config"
	"github.com/mohongen/mcp_wechat_mini/controller"
	"github.com/mohongen/mcp_wechat_mini/logger"
	"github.com/mohongen/mcp_wechat_mini/server"
)

func main() {
	// 定义命令行参数
	configPath := flag.String("config", "config.yaml", "配置文件路径")
	flag.Parse()

	// 初始化日志
	log := logger.New()
	log.Info("开始启动微信小程序数据抓取服务...")

	// 加载配置
	cfg, err := config.Load(*configPath)
	if err != nil {
		log.Fatalf("加载配置文件失败: %v", err)
	}

	// 初始化控制器
	ctrl := controller.New(log, cfg)

	// 创建并启动HTTP服务器
	srv := server.New(cfg, ctrl, log)
	go func() {
		if err := srv.Start(); err != nil {
			log.Fatalf("启动服务器失败: %v", err)
		}
	}()
	log.Infof("服务已启动，监听地址: %s", cfg.Server.Address)

	// 等待终止信号
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	log.Info("正在关闭服务...")
	if err := srv.Stop(); err != nil {
		log.Errorf("关闭服务器时出错: %v", err)
	}
	log.Info("服务已成功关闭")
}
