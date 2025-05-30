# 输入问题故障排除指南

## 🔧 解决"无法删除所有内容"的问题

如果您在运行 `python main.py` 时遇到输入框无法删除内容的问题，可以尝试以下解决方案：

### 🚀 快速解决方案

#### 方案1: 使用数字快速选择
程序现在提供预设选项，您可以：
1. 输入数字 `1` 选择"微信小程序"
2. 输入数字 `2` 选择"向僵尸小助手" 
3. 输入数字 `0` 进入手动输入模式
4. 直接按回车使用默认值

#### 方案2: 键盘快捷键
- 按 `Ctrl+A` (Windows/Linux) 或 `Cmd+A` (Mac) 全选内容
- 然后直接输入新内容覆盖
- 或者按 `Delete` 键删除选中内容

#### 方案3: 跳过输入
- 直接输入 `skip` 并按回车
- 程序将自动使用默认的"微信小程序"名称

### 🔧 配置文件解决方案

如果经常遇到输入问题，可以修改配置文件避免手动输入：

1. 打开 `app_config.py` 文件
2. 找到这一行：
   ```python
   'skip_input': False,
   ```
3. 改为：
   ```python
   'skip_input': True,
   ```
4. 可选：修改默认名称：
   ```python
   'default_app_name': '您的小程序名称',
   ```

### 🖥️ 终端环境问题

#### macOS 终端
- 尝试使用 iTerm2 替代默认终端
- 确保终端编码设置为 UTF-8

#### Windows
- 使用 Windows Terminal 替代 CMD
- 确保控制台编码正确

#### Linux
- 确保使用支持 UTF-8 的终端
- 检查 `LANG` 环境变量设置

### 🔍 其他解决方案

#### Python 环境
```bash
# 确保使用正确的 Python 版本
python --version

# 重新安装 readline (Linux/Mac)
pip install readline

# Windows 用户可以尝试
pip install pyreadline3
```

#### 备用输入方式
如果所有方法都不行，您可以：

1. **创建启动脚本**：
   ```bash
   echo "向僵尸小助手" | python main.py
   ```

2. **使用配置文件**：
   修改 `app_config.py` 中的设置跳过输入

3. **直接修改代码**：
   在 `main.py` 第 159 行左右，直接设置：
   ```python
   app_name = "您的小程序名称"  # 替换这里
   ```

### 🆘 仍然无法解决？

如果以上方法都不能解决问题，请：

1. 描述您的操作系统和终端类型
2. 提供错误信息截图
3. 说明具体的问题表现

我们会提供更具针对性的解决方案。

### 📝 预设应用列表

当前支持的快速选择选项：
1. 微信小程序
2. 向僵尸小助手  
3. 微信读书
4. 腾讯文档
5. 小程序示例

您可以在 `app_config.py` 中修改这个列表来添加您常用的小程序。 