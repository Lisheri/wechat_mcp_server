package logger

import (
	"os"

	"github.com/sirupsen/logrus"
)

// Logger 是应用程序的日志接口
type Logger interface {
	Info(args ...interface{})
	Infof(format string, args ...interface{})
	Error(args ...interface{})
	Errorf(format string, args ...interface{})
	Warn(args ...interface{})
	Warnf(format string, args ...interface{})
	Debug(args ...interface{})
	Debugf(format string, args ...interface{})
	Fatal(args ...interface{})
	Fatalf(format string, args ...interface{})
}

// logrusLogger 是对 logrus 的包装实现
type logrusLogger struct {
	*logrus.Logger
}

// New 创建并配置一个新的日志记录器
func New() Logger {
	log := logrus.New()

	// 配置日志输出为标准输出
	log.SetOutput(os.Stdout)

	// 设置日志格式
	log.SetFormatter(&logrus.TextFormatter{
		FullTimestamp:   true,
		TimestampFormat: "2006-01-02 15:04:05",
	})

	// 设置日志级别
	log.SetLevel(logrus.InfoLevel)

	return &logrusLogger{
		Logger: log,
	}
}

// 实现Logger接口方法
func (l *logrusLogger) Info(args ...interface{}) {
	l.Logger.Info(args...)
}

func (l *logrusLogger) Infof(format string, args ...interface{}) {
	l.Logger.Infof(format, args...)
}

func (l *logrusLogger) Error(args ...interface{}) {
	l.Logger.Error(args...)
}

func (l *logrusLogger) Errorf(format string, args ...interface{}) {
	l.Logger.Errorf(format, args...)
}

func (l *logrusLogger) Warn(args ...interface{}) {
	l.Logger.Warn(args...)
}

func (l *logrusLogger) Warnf(format string, args ...interface{}) {
	l.Logger.Warnf(format, args...)
}

func (l *logrusLogger) Debug(args ...interface{}) {
	l.Logger.Debug(args...)
}

func (l *logrusLogger) Debugf(format string, args ...interface{}) {
	l.Logger.Debugf(format, args...)
}

func (l *logrusLogger) Fatal(args ...interface{}) {
	l.Logger.Fatal(args...)
}

func (l *logrusLogger) Fatalf(format string, args ...interface{}) {
	l.Logger.Fatalf(format, args...)
} 