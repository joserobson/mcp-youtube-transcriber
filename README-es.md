# 🎧 YouTube MP3 Downloader & Transcriber Skill

[🇺🇸 English](README.md) | [🇧🇷 Português](README-pt.md) | [🇪🇸 Español](README-es.md) | [🇨🇳 中文](README-zh.md)

Una Skill / Herramienta lista para usar con asistentes de IA agénticos (como **Claude Code**, **Antigravity CLI**, **Codex**) y también para uso directo a través de la Línea de Comandos (CLI).

Permite descargar cualquier video o directo de YouTube en formato MP3 de alta calidad y transcribir automáticamente el contenido a texto (con marcas de tiempo) utilizando el modelo **OpenAI Whisper**.

---

## 📁 Estructura de la Skill

```text
youtube-transcriber-skill/
├── SKILL.md          # Archivo de definición de la Skill para Claude / IA
├── mcp_server.py     # Servidor MCP para integración nativa con IAs
├── ytmp3.py          # Script principal en Python (CLI)
├── requirements.txt  # Dependencias de Python
└── README.md         # Documentación y guía de uso
```

---

## 🛠️ Instalación de Dependencias

Instale todas las dependencias necesarias ejecutando:

```bash
pip install -r requirements.txt
```

> **Consejo:** `yt-dlp` detecta automáticamente si tiene `Node.js` instalado en el sistema para evitar los límites de velocidad de descarga de YouTube.

---

## 🤖 Cómo usar como Skill en Claude Code / Antigravity

Para registrarla como Skill en su asistente de IA, copie esta carpeta al directorio de skills de su proyecto o entorno global:

- **En el proyecto actual:** copie la carpeta a `.claude/skills/youtube-transcriber`
- **Globalmente en el usuario:** copie a `~/.claude/skills/youtube-transcriber`

Después de eso, simplemente pida al asistente en lenguaje natural:
- *"Descarga y transcribe el video https://youtube.com/live/..."*
- *"Extrae el MP3 de este directo y dame la transcripción con marcas de tiempo."*

---

## 🔌 Cómo usar vía MCP (Model Context Protocol)

¡El proyecto ahora soporta nativamente **MCP**! Esto significa que puede conectar esta herramienta directamente en Claude Desktop o en Cursor como herramientas oficiales, sin necesidad de escribir comandos en la terminal.

### En Claude Desktop
1. Edite el archivo de configuración de Claude Desktop:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Añada el servidor apuntando al script Python local:
```json
{
  "mcpServers": {
    "youtube-transcriber": {
      "command": "python",
      "args": ["RUTA_ABSOLUTA_AQUI/youtube-transcriber-skill/mcp_server.py"]
    }
  }
}
```
3. Reinicie Claude Desktop. Claude ahora tendrá las herramientas `download_youtube_audio`, `transcribe_audio`, etc.

### En Cursor IDE
1. Abra las Configuraciones de Cursor > **Features** > **MCP**.
2. Haga clic en **+ Add New MCP Server**.
3. Seleccione el tipo **command**.
4. Escriba: `python RUTA_ABSOLUTA_AQUI/youtube-transcriber-skill/mcp_server.py`

---

## 💻 Cómo usar vía Línea de Comandos (CLI)

También puede utilizar el script `ytmp3.py` directamente:

### 1. Transcribir Video o Directo a Texto
```bash
python ytmp3.py transcribe "https://youtube.com/live/FL_ID" --timestamps -m small -l pt
```

### 2. Solo Descargar el MP3
```bash
python ytmp3.py download "https://youtube.com/watch?v=XYZ" -o "mi_cancion.mp3"
```

### 3. Cortar Fragmentos del MP3
```bash
python ytmp3.py cut "mi_cancion.mp3" 0:30 2:45 -o "corte.mp3"
```

### 4. Modo Automático (Descargar + Cortar Fragmentos Específicos)
```bash
python ytmp3.py auto "https://youtube.com/watch?v=XYZ" 0:00-1:30 4:00-end -o "editado.mp3"
```

---

## 📜 Licencia

¡Siéntase libre de usar, modificar y subir a su GitHub!
