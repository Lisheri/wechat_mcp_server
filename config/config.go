package config

import (
	"os"
	"time"

	"gopkg.in/yaml.v3"
)

// Config 保存整个应用的配置信息
type Config struct {
	Server   ServerConfig   `yaml:"server"`
	Wechat   WechatConfig   `yaml:"wechat"`
	Scraper  ScraperConfig  `yaml:"scraper"`
	Database DatabaseConfig `yaml:"database"`
}

// ServerConfig HTTP服务器配置
type ServerConfig struct {
	Address      string        `yaml:"address"`
	ReadTimeout  time.Duration `yaml:"readTimeout"`
	WriteTimeout time.Duration `yaml:"writeTimeout"`
}

// WechatConfig 微信小程序相关配置
type WechatConfig struct {
	AppID     string `yaml:"appID"`
	AppSecret string `yaml:"appSecret"`
}

// ScraperConfig 数据抓取配置
type ScraperConfig struct {
	UserAgent      string        `yaml:"userAgent"`
	Timeout        time.Duration `yaml:"timeout"`
	MaxConcurrency int           `yaml:"maxConcurrency"`
	RetryTimes     int           `yaml:"retryTimes"`
	RetryDelay     time.Duration `yaml:"retryDelay"`
}

// DatabaseConfig 数据库配置
type DatabaseConfig struct {
	Type     string `yaml:"type"`
	Host     string `yaml:"host"`
	Port     int    `yaml:"port"`
	User     string `yaml:"user"`
	Password string `yaml:"password"`
	DBName   string `yaml:"dbName"`
}

// Load 从文件加载配置
func Load(path string) (*Config, error) {
	// 读取配置文件
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	// 解析YAML配置
	var cfg Config
	if err := yaml.Unmarshal(data, &cfg); err != nil {
		return nil, err
	}

	// 设置默认值
	setDefaults(&cfg)

	return &cfg, nil
}

// setDefaults 设置配置的默认值
func setDefaults(cfg *Config) {
	// 服务器默认配置
	if cfg.Server.Address == "" {
		cfg.Server.Address = ":8080"
	}
	if cfg.Server.ReadTimeout == 0 {
		cfg.Server.ReadTimeout = 10 * time.Second
	}
	if cfg.Server.WriteTimeout == 0 {
		cfg.Server.WriteTimeout = 10 * time.Second
	}

	// 爬虫默认配置
	if cfg.Scraper.UserAgent == "" {
		cfg.Scraper.UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1"
	}
	if cfg.Scraper.Timeout == 0 {
		cfg.Scraper.Timeout = 30 * time.Second
	}
	if cfg.Scraper.MaxConcurrency == 0 {
		cfg.Scraper.MaxConcurrency = 5
	}
	if cfg.Scraper.RetryTimes == 0 {
		cfg.Scraper.RetryTimes = 3
	}
	if cfg.Scraper.RetryDelay == 0 {
		cfg.Scraper.RetryDelay = 2 * time.Second
	}
} 