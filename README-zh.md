# 🎧 YouTube MP3 Downloader & Transcriber Skill

[🇺🇸 English](README.md) | [🇧🇷 Português](README-pt.md) | [🇪🇸 Español](README-es.md) | [🇨🇳 中文](README-zh.md)

一个开箱即用的 Skill / 工具，专为智能体 AI 助手（如 **Claude Code**、**Antigravity CLI**、**Codex**）设计，同时也支持直接通过命令行 (CLI) 使用。

它允许您以高质量的 MP3 格式下载任何 YouTube 视频或直播，并使用 **OpenAI Whisper** 模型自动将内容转录为文本（带时间戳）。

---

## 📁 Skill 结构

```text
youtube-transcriber-skill/
├── SKILL.md          # 供 Claude / AI 识别的 Skill 定义文件
├── mcp_server.py     # 用于原生 AI 集成的 MCP 服务器
├── ytmp3.py          # 主 Python 脚本 (CLI)
├── requirements.txt  # Python 依赖项
└── README.md         # 文档和使用指南
```

---

## 🛠️ 安装依赖项

通过运行以下命令安装所有必需的依赖项：

```bash
pip install -r requirements.txt
```

> **提示：** `yt-dlp` 会自动检测您的系统是否安装了 `Node.js`，以绕过 YouTube 的下载速度限制。

---

## 🤖 如何在 Claude Code / Antigravity 中作为 Skill 使用

要将其注册为您的 AI 助手的 Skill，请将此文件夹复制到项目或全局的 skills 目录中：

- **当前项目：** 将文件夹复制到 `.claude/skills/youtube-transcriber`
- **全局用户：** 复制到 `~/.claude/skills/youtube-transcriber`

之后，只需用自然语言向助手提问：
- *"下载并转录视频 https://youtube.com/live/..."*
- *"提取此直播的 MP3 并提供带时间戳的转录文本。"*

---

## 🔌 如何通过 MCP (Model Context Protocol) 使用

该项目现在原生支持 **MCP**！这意味着您可以将此工具作为官方工具直接插入 Claude Desktop 或 Cursor 中，而无需在终端中键入命令。

### 在 Claude Desktop 中
1. 编辑 Claude Desktop 配置文件：
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. 添加指向本地 Python 脚本的服务器：
```json
{
  "mcpServers": {
    "youtube-transcriber": {
      "command": "python",
      "args": ["这里填写绝对路径/youtube-transcriber-skill/mcp_server.py"]
    }
  }
}
```
3. 重启 Claude Desktop。Claude 现在将具有 `download_youtube_audio`、`transcribe_audio` 等工具。

### 在 Cursor IDE 中
1. 打开 Cursor 设置 > **Features** > **MCP**。
2. 单击 **+ Add New MCP Server**。
3. 选择类型 **command**。
4. 键入：`python 这里填写绝对路径/youtube-transcriber-skill/mcp_server.py`

---

## 💻 如何通过命令行 (CLI) 使用

您也可以直接使用 `ytmp3.py` 脚本：

### 1. 将视频或直播转录为文本
```bash
python ytmp3.py transcribe "https://youtube.com/live/FL_ID" --timestamps -m small -l pt
```

### 2. 仅下载 MP3
```bash
python ytmp3.py download "https://youtube.com/watch?v=XYZ" -o "my_song.mp3"
```

### 3. 剪切 MP3 片段
```bash
python ytmp3.py cut "my_song.mp3" 0:30 2:45 -o "cut.mp3"
```

### 4. 自动模式（下载 + 剪切特定片段）
```bash
python ytmp3.py auto "https://youtube.com/watch?v=XYZ" 0:00-1:30 4:00-end -o "edited.mp3"
```

---

## 📜 许可证

请随意使用、修改并推送到您的 GitHub！
