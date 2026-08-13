# 🎧 YouTube MP3 Downloader & Transcriber Skill

[🇺🇸 English](README.md) | [🇧🇷 Português](README-pt.md) | [🇪🇸 Español](README-es.md) | [🇨🇳 中文](README-zh.md)

A ready-to-use Skill / Tool for agentic AI assistants (such as **Claude Code**, **Antigravity CLI**, **Codex**) and also for direct Command Line (CLI) usage.

It allows you to download any YouTube video or livestream in high-quality MP3 format and automatically transcribe the content into text (with timestamps) using the **OpenAI Whisper** model.

---

## 📁 Skill Structure

```text
youtube-transcriber-skill/
├── SKILL.md          # Skill definition file for Claude / AI
├── mcp_server.py     # MCP Server for native AI integration
├── ytmp3.py          # Main Python script (CLI)
├── requirements.txt  # Python dependencies
└── README.md         # Documentation and user guide
```

---

## 🛠️ Installing Dependencies

Install all necessary dependencies by running:

```bash
pip install -r requirements.txt
```

> **Tip:** `yt-dlp` automatically detects if you have `Node.js` installed on your system to bypass YouTube's download speed limits.

---

## 🤖 How to use as a Skill in Claude Code / Antigravity

To register this as a Skill in your AI assistant, copy this folder to your project's or global skills directory:

- **Current project:** copy the folder to `.claude/skills/youtube-transcriber`
- **Global user:** copy to `~/.claude/skills/youtube-transcriber`

After that, simply ask the assistant in natural language:
- *"Download and transcribe the video https://youtube.com/live/..."*
- *"Extract the MP3 from this livestream and give me the transcription with timestamps."*

---

## 🔌 How to use via MCP (Model Context Protocol)

The project now natively supports **MCP**! This means you can plug this tool directly into Claude Desktop or Cursor as official tools, without needing to type terminal commands.

### In Claude Desktop
1. Edit the Claude Desktop configuration file:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Add the server pointing to the local Python script:
```json
{
  "mcpServers": {
    "youtube-transcriber": {
      "command": "python",
      "args": ["ABSOLUTE_PATH_HERE/youtube-transcriber-skill/mcp_server.py"]
    }
  }
}
```
3. Restart Claude Desktop. Claude will now have the tools `download_youtube_audio`, `transcribe_audio`, etc.

### In Cursor IDE
1. Open Cursor Settings > **Features** > **MCP**.
2. Click on **+ Add New MCP Server**.
3. Select the type **command**.
4. Type: `python ABSOLUTE_PATH_HERE/youtube-transcriber-skill/mcp_server.py`

---

## 💻 How to use via Command Line (CLI)

You can also use the `ytmp3.py` script directly:

### 1. Transcribe Video or Livestream to Text
```bash
python ytmp3.py transcribe "https://youtube.com/live/FL_ID" --timestamps -m small -l pt
```

### 2. Just Download the MP3
```bash
python ytmp3.py download "https://youtube.com/watch?v=XYZ" -o "my_song.mp3"
```

### 3. Cut MP3 Segments
```bash
python ytmp3.py cut "my_song.mp3" 0:30 2:45 -o "cut.mp3"
```

### 4. Auto Mode (Download + Cut Specific Segments)
```bash
python ytmp3.py auto "https://youtube.com/watch?v=XYZ" 0:00-1:30 4:00-end -o "edited.mp3"
```

---

## 📜 License

Feel free to use, modify, and push to your GitHub!
