import sys
import os
import subprocess
from mcp.server.fastmcp import FastMCP

# Cria o servidor MCP
mcp = FastMCP("YouTube Transcriber")

# O diretório atual onde o script está
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
YTMP3_SCRIPT = os.path.join(BASE_DIR, "ytmp3.py")

def run_cli_command(args):
    """Função auxiliar para rodar o ytmp3.py e capturar a saída sem quebrar o MCP stdio."""
    cmd = [sys.executable, YTMP3_SCRIPT] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=BASE_DIR, encoding='utf-8')
    if result.returncode != 0:
        return f"Erro ao executar comando:\n{result.stderr}\n{result.stdout}"
    return f"Sucesso:\n{result.stdout}"

@mcp.tool()
def download_youtube_audio(url: str, output: str = None) -> str:
    """
    Baixa um vídeo do YouTube e converte para MP3.
    
    Args:
        url: A URL do vídeo do YouTube.
        output: Opcional. Nome do arquivo MP3 de saída.
    """
    args = ["download", url]
    if output:
        args.extend(["-o", output])
    return run_cli_command(args)

@mcp.tool()
def transcribe_audio(source: str, model: str = "small", language: str = "pt", timestamps: bool = False) -> str:
    """
    Transcreve áudio de um arquivo MP3 local ou URL do YouTube para texto.
    
    Args:
        source: URL do YouTube ou caminho local do arquivo MP3.
        model: Modelo do Whisper ('tiny', 'base', 'small', 'medium', 'large').
        language: Idioma ('pt', 'en', 'es', 'auto').
        timestamps: Se True, inclui marcas de tempo [HH:MM:SS] no texto.
    """
    args = ["transcribe", source, "-m", model, "-l", language]
    if timestamps:
        args.append("--timestamps")
    return run_cli_command(args)

@mcp.tool()
def cut_audio(input_file: str, start: str, end: str, output: str = None) -> str:
    """
    Corta um trecho do MP3.
    
    Args:
        input_file: Arquivo MP3 local.
        start: Tempo inicial (ex: '0:00', '90').
        end: Tempo final (ex: '1:30', 'end').
        output: Opcional. Arquivo MP3 de saída.
    """
    args = ["cut", input_file, start, end]
    if output:
        args.extend(["-o", output])
    return run_cli_command(args)

@mcp.tool()
def auto_youtube_workflow(url: str, segments: list[str], output: str = None) -> str:
    """
    Baixa do YouTube, aplica cortes específicos e junta tudo em um único arquivo.
    
    Args:
        url: URL do vídeo.
        segments: Lista de segmentos no formato 'START-END' (ex: ['0:00-1:00', '2:30-end']).
        output: Opcional. Arquivo MP3 final.
    """
    args = ["auto", url]
    args.extend(segments)
    if output:
        args.extend(["-o", output])
    return run_cli_command(args)

if __name__ == "__main__":
    mcp.run(transport="stdio")
