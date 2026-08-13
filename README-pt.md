# 🎧 YouTube MP3 Downloader & Transcriber Skill

[🇺🇸 English](README.md) | [🇧🇷 Português](README-pt.md) | [🇪🇸 Español](README-es.md) | [🇨🇳 中文](README-zh.md)

Uma Skill / Ferramenta pronta para assistentes de IA agênticos (como **Claude Code**, **Antigravity CLI**, **Codex**) e também para uso direto via Linha de Comando (CLI).

Ela permite baixar qualquer vídeo ou live do YouTube em formato MP3 de alta qualidade e transcrever automaticamente o conteúdo em texto (com timestamps) utilizando o modelo **OpenAI Whisper**.

---

## 📁 Estrutura da Skill

```text
youtube-transcriber-skill/
├── SKILL.md          # Arquivo de definição da Skill para o Claude / IA
├── mcp_server.py     # Servidor MCP para integração nativa com IAs
├── ytmp3.py          # Script principal em Python (CLI)
├── requirements.txt  # Dependências do Python
└── README.md         # Documentação e guia de uso
```

---

## 🛠️ Instalação das Dependências

Instale todas as dependências necessárias executando:

```bash
pip install -r requirements.txt
```

> **Dica:** O `yt-dlp` detecta automaticamente se você tem o `Node.js` instalado no sistema para contornar limitações de velocidade de download do YouTube.

---

## 🤖 Como Usar como Skill no Claude Code / Antigravity

Para registrar como Skill no seu assistente de IA, copie esta pasta para o diretório de skills do seu projeto ou ambiente global:

- **No projeto atual:** copie a pasta para `.claude/skills/youtube-transcriber`
- **Globalmente no usuário:** copie para `~/.claude/skills/youtube-transcriber`

Depois disso, basta pedir ao assistente em linguagem natural:
- *"Baixe e transcreva o vídeo https://youtube.com/live/..."*
- *"Extraia o MP3 dessa live e me dê a transcrição com marcas de tempo."*

---

## 🔌 Como Usar via MCP (Model Context Protocol)

O projeto agora suporta nativamente o **MCP**! Isso significa que você pode plugar esta ferramenta diretamente no Claude Desktop ou no Cursor como ferramentas oficiais, sem precisar digitar comandos no terminal.

### No Claude Desktop
1. Edite o arquivo de configuração do Claude Desktop:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Adicione o servidor apontando para o script Python local:
```json
{
  "mcpServers": {
    "youtube-transcriber": {
      "command": "python",
      "args": ["CAMINHO_ABSOLUTO_AQUI/youtube-transcriber-skill/mcp_server.py"]
    }
  }
}
```
3. Reinicie o Claude Desktop. O Claude agora terá as ferramentas `download_youtube_audio`, `transcribe_audio`, etc.

### No Cursor IDE
1. Abra as Configurações do Cursor > **Features** > **MCP**.
2. Clique em **+ Add New MCP Server**.
3. Selecione o tipo **command**.
4. Digite: `python CAMINHO_ABSOLUTO_AQUI/youtube-transcriber-skill/mcp_server.py`

---

## 💻 Como Usar via Linha de Comando (CLI)

Você também pode utilizar o script `ytmp3.py` diretamente:

### 1. Transcrever Vídeo ou Live para Texto
```bash
python ytmp3.py transcribe "https://youtube.com/live/FL_ID" --timestamps -m small -l pt
```

### 2. Apenas Baixar o MP3
```bash
python ytmp3.py download "https://youtube.com/watch?v=XYZ" -o "minha_musica.mp3"
```

### 3. Cortar Trechos do MP3
```bash
python ytmp3.py cut "minha_musica.mp3" 0:30 2:45 -o "corte.mp3"
```

### 4. Modo Automático (Baixar + Cortar Trechos Específicos)
```bash
python ytmp3.py auto "https://youtube.com/watch?v=XYZ" 0:00-1:30 4:00-end -o "editado.mp3"
```

---

## 📜 Licença

Sinta-se à vontade para utilizar, modificar e subir para o seu GitHub!
