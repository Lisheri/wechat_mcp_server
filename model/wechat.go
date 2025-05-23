package model

import "time"

// MiniProgramPage 表示微信小程序页面数据
type MiniProgramPage struct {
	ID        int64      `json:"id"`
	AppID     string     `json:"appId"`     // 小程序的AppID
	PagePath  string     `json:"pagePath"`  // 小程序页面路径
	Title     string     `json:"title"`     // 页面标题
	Content   string     `json:"content"`   // 页面HTML内容
	Screenshot string    `json:"screenshot"` // 页面截图（Base64编码）
	CreatedAt time.Time  `json:"createdAt"` // 创建时间
	UpdatedAt time.Time  `json:"updatedAt"` // 更新时间
	Metadata  PageMetadata `json:"metadata"` // 页面元数据
}

// PageMetadata 页面的元数据
type PageMetadata struct {
	Components []ComponentInfo `json:"components"` // 页面组件信息
	APIs       []APIInfo       `json:"apis"`       // 页面使用的API
	Resources  []ResourceInfo  `json:"resources"`  // 页面资源
}

// ComponentInfo 组件信息
type ComponentInfo struct {
	Name      string            `json:"name"`      // 组件名称
	Count     int               `json:"count"`     // 组件数量
	Props     map[string]string `json:"props"`     // 组件属性
	Location  string            `json:"location"`  // 组件在页面中的位置
}

// APIInfo API调用信息
type APIInfo struct {
	Name       string            `json:"name"`       // API名称
	Parameters map[string]string `json:"parameters"` // API参数
	URL        string            `json:"url"`        // API请求URL
}

// ResourceInfo 资源信息
type ResourceInfo struct {
	Type     string `json:"type"`     // 资源类型 (image, video, audio等)
	URL      string `json:"url"`      // 资源URL
	Size     int64  `json:"size"`     // 资源大小(字节)
	MimeType string `json:"mimeType"` // MIME类型
}

// ScrapRequest 抓取页面的请求参数
type ScrapRequest struct {
	AppID    string `json:"appId"`    // 小程序的AppID
	PagePath string `json:"pagePath"` // 页面路径
	Params   map[string]string `json:"params"` // 页面参数
	Options  ScrapOptions `json:"options"`     // 抓取选项
}

// ScrapOptions 抓取选项
type ScrapOptions struct {
	ScreenshotEnabled bool `json:"screenshotEnabled"` // 是否需要截图
	MetadataEnabled   bool `json:"metadataEnabled"`   // 是否需要元数据
	MaxWaitTime       int  `json:"maxWaitTime"`       // 最大等待时间(秒)
}

// ScrapResponse 抓取结果
type ScrapResponse struct {
	Success  bool           `json:"success"`  // 是否成功
	Message  string         `json:"message"`  // 消息
	Data     MiniProgramPage `json:"data"`    // 抓取到的数据
	Duration int64          `json:"duration"` // 耗时(毫秒)
} 