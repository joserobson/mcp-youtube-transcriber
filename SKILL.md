---
name: youtube-transcriber
description: Baixa áudios em MP3 de vídeos do YouTube e realiza transcrição automática de voz para texto com marcas de tempo (timestamps) usando Whisper.
---

# YouTube Transcriber & MP3 Converter Skill

Esta skill permite baixar o áudio em formato MP3 de qualquer vídeo ou live do YouTube, além de realizar a transcrição automática do áudio para texto em português (ou outro idioma) utilizando a biblioteca OpenAI Whisper.

## Quando usar esta Skill

Use esta skill quando o usuário solicitar:
- "Baixe o áudio/MP3 deste vídeo do YouTube: <URL>"
- "Transcreva o vídeo do YouTube: <URL>"
- "Corte o áudio do vídeo do YouTube entre [tempo1] e [tempo2]"
- "Converta o áudio do vídeo para MP3 e faça o resumo/transcrição"

## Pré-requisitos
Certifique-se de que os pacotes do `requirements.txt` estão instalados:
```bash
pip install -r requirements.txt
```
Opcional para desacelerar throttling do YouTube: Node.js instalado no sistema (detectado automaticamente pelo `yt-dlp`).

---

## Comandos Disponíveis

### 1. Transcrever Vídeo do YouTube para Texto (com Timestamps)
```bash
python ytmp3.py transcribe "<URL_DO_VIDEO>" --timestamps -m small -l pt
```
- Opções de modelo (`-m`): `tiny`, `base`, `small` (padrão), `medium`, `large`.
- Idioma (`-l`): `pt` (padrão), `en`, `es`, `auto`.
- O resultado `.txt` é gerado na pasta `output/`.

### 2. Apenas Baixar o Áudio MP3
```bash
python ytmp3.py download "<URL_DO_VIDEO>" -o "nome_do_arquivo.mp3"
```
- O arquivo é salvo automaticamente na pasta `output/`.

### 3. Cortar Trechos do MP3
```bash
python ytmp3.py cut "output/musica.mp3" 0:00 2:30 -o "corte.mp3"
```

### 4. Modo Automático (Baixar + Cortar Trechos Específicos)
```bash
python ytmp3.py auto "<URL_DO_VIDEO>" 0:00-2:00 5:30-end -o "resultado_final.mp3"
```

---

## Diretório de Saída
Todos os arquivos MP3 e transcrições geradas são salvos por padrão no diretório `output/`.
