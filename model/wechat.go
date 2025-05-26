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

// ScreenshotAnalysisRequest 基于截图分析的请求参数
type ScreenshotAnalysisRequest struct {
	ScreenshotBase64 string                    `json:"screenshotBase64"` // Base64编码的截图
	AnalysisOptions  ScreenshotAnalysisOptions `json:"analysisOptions"`  // 分析选项
}

// ScreenshotAnalysisOptions 截图分析选项
type ScreenshotAnalysisOptions struct {
	ExtractText      bool `json:"extractText"`      // 是否提取文本
	DetectButtons    bool `json:"detectButtons"`    // 是否检测按钮
	DetectIcons      bool `json:"detectIcons"`      // 是否检测图标
	AnalyzeLayout    bool `json:"analyzeLayout"`    // 是否分析布局
	ExtractColors    bool `json:"extractColors"`    // 是否提取颜色信息
}

// ScreenshotAnalysisResponse 截图分析结果
type ScreenshotAnalysisResponse struct {
	Success     bool                    `json:"success"`     // 是否成功
	Message     string                  `json:"message"`     // 消息
	Data        ScreenshotAnalysisData  `json:"data"`        // 分析数据
	Duration    int64                   `json:"duration"`    // 耗时(毫秒)
}

// ScreenshotAnalysisData 截图分析的数据
type ScreenshotAnalysisData struct {
	ExtractedTexts  []TextElement    `json:"extractedTexts"`  // 提取的文本
	DetectedButtons []ButtonElement  `json:"detectedButtons"` // 检测到的按钮
	DetectedIcons   []IconElement    `json:"detectedIcons"`   // 检测到的图标
	LayoutInfo      LayoutInfo       `json:"layoutInfo"`      // 布局信息
	ColorPalette    []ColorInfo      `json:"colorPalette"`    // 颜色信息
	Summary         string           `json:"summary"`         // 页面总结
}

// TextElement 文本元素
type TextElement struct {
	Text       string    `json:"text"`       // 文本内容
	Position   Position  `json:"position"`   // 位置信息
	Confidence float64   `json:"confidence"` // 识别置信度
	FontSize   int       `json:"fontSize"`   // 字体大小（估算）
}

// ButtonElement 按钮元素
type ButtonElement struct {
	Text     string   `json:"text"`     // 按钮文本
	Position Position `json:"position"` // 位置信息
	Type     string   `json:"type"`     // 按钮类型（primary, secondary等）
}

// IconElement 图标元素
type IconElement struct {
	Description string   `json:"description"` // 图标描述
	Position    Position `json:"position"`    // 位置信息
	Category    string   `json:"category"`    // 图标分类
}

// Position 位置信息
type Position struct {
	X      int `json:"x"`      // X坐标
	Y      int `json:"y"`      // Y坐标
	Width  int `json:"width"`  // 宽度
	Height int `json:"height"` // 高度
}

// LayoutInfo 布局信息
type LayoutInfo struct {
	Sections    []LayoutSection `json:"sections"`    // 页面区域
	GridLayout  bool            `json:"gridLayout"`  // 是否为网格布局
	Columns     int             `json:"columns"`     // 列数
	Rows        int             `json:"rows"`        // 行数
}

// LayoutSection 布局区域
type LayoutSection struct {
	Name     string   `json:"name"`     // 区域名称
	Position Position `json:"position"` // 位置信息
	Type     string   `json:"type"`     // 区域类型（header, content, footer等）
}

// ColorInfo 颜色信息
type ColorInfo struct {
	Color      string  `json:"color"`      // 颜色值（HEX）
	Percentage float64 `json:"percentage"` // 占比
	Usage      string  `json:"usage"`      // 用途（background, text, accent等）
} 