#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ytmp3 - YouTube to MP3 converter with cut, merge and transcription support.

Usage examples:
  python ytmp3.py download "https://youtube.com/watch?v=..." -o song.mp3
  python ytmp3.py cut song.mp3 0:00 2:00 -o part1.mp3
  python ytmp3.py cut song.mp3 3:00 end -o part2.mp3
  python ytmp3.py merge part1.mp3 part2.mp3 -o final.mp3
  python ytmp3.py auto "https://youtube.com/watch?v=..." 0:00-2:00 3:00-end -o final.mp3
  python ytmp3.py transcribe musica.mp3
  python ytmp3.py transcribe "https://youtube.com/watch?v=..." -m medium
"""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Fix Windows terminal encoding
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import click
from pydub import AudioSegment
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich.text import Text

console = Console()

OUTPUT_DIR = Path(__file__).parent / "output"


def _out(filename: str) -> str:
    """Resolve output path: if filename has no directory, place it in OUTPUT_DIR."""
    p = Path(filename)
    if p.parent == Path("."):
        OUTPUT_DIR.mkdir(exist_ok=True)
        return str(OUTPUT_DIR / p.with_suffix(".mp3").name)
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p.with_suffix(".mp3"))


def parse_time(time_str: str, total_duration_ms: int | None = None) -> int:
    """
    Parse time string to milliseconds.
    Formats accepted: 'end', '1:30', '0:02:30', '90' (seconds), '90.5'
    """
    time_str = time_str.strip().lower()

    if time_str == "end":
        if total_duration_ms is None:
            raise click.BadParameter("'end' requires knowing the total duration. Load the audio first.")
        return total_duration_ms

    # Try mm:ss or hh:mm:ss
    if ":" in time_str:
        parts = time_str.split(":")
        if len(parts) == 2:
            minutes, seconds = parts
            total_seconds = int(minutes) * 60 + float(seconds)
        elif len(parts) == 3:
            hours, minutes, seconds = parts
            total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
        else:
            raise click.BadParameter(f"Invalid time format: '{time_str}'. Use mm:ss, hh:mm:ss, or seconds.")
        return int(total_seconds * 1000)

    # Try plain seconds
    try:
        return int(float(time_str) * 1000)
    except ValueError:
        raise click.BadParameter(
            f"Invalid time format: '{time_str}'. Use 'end', 'mm:ss', 'hh:mm:ss', or seconds."
        )


def format_duration(ms: int) -> str:
    total_seconds = ms // 1000
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    return f"{minutes}:{seconds:02d}"


def _get_node_path() -> str | None:
    """Find node.js executable path."""
    import shutil
    return shutil.which("node") or shutil.which("node.exe")


def _yt_dlp_cmd(extra_args: list[str], url: str) -> list[str]:
    """Build base yt-dlp command with JS runtime and anti-429 extractor args."""
    node_path = _get_node_path()
    cmd = [sys.executable, "-X", "utf8", "-m", "yt_dlp", "-4"]
    if node_path:
        cmd += ["--js-runtimes", f"node:{node_path}", "--remote-components", "ejs:github"]

    # Avoid HTTP 429 on webpage/initial_data endpoints and web client bot check
    cmd += [
        "--extractor-args",
        "youtube:player_client=android;player_skip=webpage,initial_data,configs",
    ]

    cookies_file = os.environ.get("YTMP3_COOKIES") or str(Path(__file__).parent / "cookies.txt")
    cookies_browser = os.environ.get("YTMP3_COOKIES_BROWSER")
    if Path(cookies_file).is_file():
        cmd += ["--cookies", cookies_file]
    elif cookies_browser:
        cmd += ["--cookies-from-browser", cookies_browser]

    cmd += extra_args + [url]
    return cmd


def _run(cmd: list[str]) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if result.returncode != 0:
        err = result.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(err or "yt-dlp failed")
    return result


def get_video_title(url: str) -> str:
    """Get video title without downloading."""
    cmd = _yt_dlp_cmd(["--print", "title", "--no-playlist", "--no-download"], url)
    result = _run(cmd)
    out = result.stdout.decode("utf-8", errors="replace").strip()
    return out.splitlines()[0] if out else "audio"


def download_audio(url: str, output_path: str) -> str:
    """Download audio from YouTube URL using yt-dlp via subprocess."""
    output_path = str(Path(output_path).with_suffix(""))  # yt-dlp adds extension

    cmd = _yt_dlp_cmd([
        "--print", "title",
        "--no-simulate",
        "--http-chunk-size", "10M",
        "--format", "bestaudio/best",
        "--output", output_path,
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "192K",
        "--no-playlist",
    ], url)

    result = _run(cmd)
    out = result.stdout.decode("utf-8", errors="replace").strip()
    return out.splitlines()[0] if out else "audio"


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

@click.group()
def cli():
    """ytmp3 - Converta YouTube para MP3, corte e junte trechos."""
    pass


# ── DOWNLOAD ──────────────────────────────────

@cli.command()
@click.argument("url")
@click.option("-o", "--output", default=None, help="Nome do arquivo de saída (padrão: título do vídeo).")
def download(url: str, output: str | None):
    """Baixa um vídeo do YouTube e converte para MP3.

    \b
    Exemplo:
      python ytmp3.py download "https://youtube.com/watch?v=XYZ" -o musica.mp3
    """
    console.print(Panel(f"[bold cyan]Baixando:[/] {url}", title="ytmp3 download"))

    # Download to a temp path first to get the title, then rename
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_out = os.path.join(tmpdir, "audio.mp3")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Baixando e convertendo para MP3...", total=None)
            title = download_audio(url, tmp_out)
            progress.update(task, description=f"Concluído: {title}")

        _save_title(url, title)
        final_name = output if output else (_sanitize(title) + ".mp3")
        final_path = _out(final_name)
        import shutil
        shutil.copyfile(tmp_out, final_path)

    audio = AudioSegment.from_mp3(final_path)
    console.print(
        f"[green]✓[/] Salvo em [bold]{final_path}[/] "
        f"([dim]{format_duration(len(audio))}[/])"
    )


# ── CUT ───────────────────────────────────────

@cli.command()
@click.argument("input_file")
@click.argument("start")
@click.argument("end")
@click.option("-o", "--output", default=None, help="Nome do arquivo de saída (padrão: <input>_cut.mp3).")
def cut(input_file: str, start: str, end: str, output: str | None):
    """Corta um trecho do MP3 entre START e END.

    \b
    Formatos de tempo aceitos:
      mm:ss    ex: 1:30
      hh:mm:ss ex: 0:01:30
      segundos ex: 90
      'end'    para o fim do arquivo

    \b
    Exemplos:
      python ytmp3.py cut musica.mp3 0:00 2:00 -o parte1.mp3
      python ytmp3.py cut musica.mp3 3:00 end  -o parte2.mp3
    """
    if not Path(input_file).exists():
        console.print(f"[red]Erro:[/] Arquivo não encontrado: {input_file}")
        sys.exit(1)

    if output is None:
        output = f"{Path(input_file).stem}_cut.mp3"
    output = _out(output)

    console.print(Panel(f"[bold cyan]Cortando:[/] {input_file}", title="ytmp3 cut"))

    audio = AudioSegment.from_mp3(input_file)
    duration_ms = len(audio)

    start_ms = parse_time(start, duration_ms)
    end_ms = parse_time(end, duration_ms)

    if start_ms >= end_ms:
        console.print(f"[red]Erro:[/] START ({start}) deve ser menor que END ({end}).")
        sys.exit(1)

    if end_ms > duration_ms:
        console.print(
            f"[yellow]Aviso:[/] END ({format_duration(end_ms)}) excede a duração "
            f"({format_duration(duration_ms)}). Usando o fim do arquivo."
        )
        end_ms = duration_ms

    segment = audio[start_ms:end_ms]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Exportando...", total=None)
        segment.export(output, format="mp3", bitrate="192k")
        progress.update(task, description="Concluído")

    console.print(
        f"[green]✓[/] Trecho [bold]{format_duration(start_ms)}[/] → "
        f"[bold]{format_duration(end_ms)}[/] salvo em [bold]{output}[/] "
        f"([dim]{format_duration(len(segment))}[/])"
    )


# ── MERGE ─────────────────────────────────────

@cli.command()
@click.argument("files", nargs=-1, required=True)
@click.option("-o", "--output", default="merged.mp3", show_default=True, help="Nome do arquivo de saída.")
def merge(files: tuple[str, ...], output: str):
    """Junta múltiplos arquivos MP3 em um só (na ordem fornecida).

    \b
    Exemplo:
      python ytmp3.py merge parte1.mp3 parte2.mp3 -o final.mp3
      python ytmp3.py merge a.mp3 b.mp3 c.mp3 -o completo.mp3
    """
    for f in files:
        if not Path(f).exists():
            console.print(f"[red]Erro:[/] Arquivo não encontrado: {f}")
            sys.exit(1)

    output = _out(output)
    console.print(Panel(f"[bold cyan]Juntando {len(files)} arquivo(s)[/]", title="ytmp3 merge"))

    combined = AudioSegment.empty()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Carregando arquivos...", total=len(files))
        for f in files:
            audio = AudioSegment.from_mp3(f)
            combined += audio
            progress.advance(task)
            progress.update(task, description=f"Adicionado: {f}")

        progress.update(task, description="Exportando resultado final...")
        combined.export(output, format="mp3", bitrate="192k")

    console.print(
        f"[green]✓[/] {len(files)} arquivos juntados em [bold]{output}[/] "
        f"([dim]{format_duration(len(combined))}[/])"
    )


# ── AUTO ──────────────────────────────────────

def _extract_video_id(url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    import re
    patterns = [
        r"(?:v=|youtu\.be/)([A-Za-z0-9_-]{11})",
        r"(?:embed/|shorts/)([A-Za-z0-9_-]{11})",
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None


def _sanitize(name: str) -> str:
    """Remove characters invalid in filenames."""
    import re
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    name = name.strip(". ")
    return name or "audio"


def _cache_dir() -> Path:
    d = Path(__file__).parent / ".cache"
    d.mkdir(exist_ok=True)
    return d


def _cache_path(url: str) -> Path | None:
    """Return the cache MP3 path for a given URL, or None if ID can't be extracted."""
    video_id = _extract_video_id(url)
    if not video_id:
        return None
    return _cache_dir() / f"{video_id}.mp3"


def _title_path(url: str) -> Path | None:
    """Return path to the cached title file for a given URL."""
    video_id = _extract_video_id(url)
    if not video_id:
        return None
    return _cache_dir() / f"{video_id}.title"


def _save_title(url: str, title: str) -> None:
    tp = _title_path(url)
    if tp:
        tp.write_text(title, encoding="utf-8")


def _load_title(url: str) -> str | None:
    tp = _title_path(url)
    if tp and tp.exists():
        return tp.read_text(encoding="utf-8").strip()
    return None


def _cut_and_merge(source_mp3: str, parsed_segments: list[tuple[str, str]], output: str) -> int:
    """Cut segments from source_mp3 and merge into output. Returns total merged duration in ms."""
    audio = AudioSegment.from_mp3(source_mp3)
    duration_ms = len(audio)
    console.print(f"Duração total: [bold]{format_duration(duration_ms)}[/]")

    combined = AudioSegment.empty()
    for i, (start_str, end_str) in enumerate(parsed_segments, 1):
        start_ms = parse_time(start_str, duration_ms)
        end_ms = parse_time(end_str, duration_ms)

        if start_ms >= end_ms:
            console.print(f"[red]Erro:[/] Segmento {i}: START >= END ({start_str} >= {end_str}).")
            sys.exit(1)

        end_ms = min(end_ms, duration_ms)
        segment = audio[start_ms:end_ms]
        combined += segment

        console.print(
            f"  [green]✓[/] Segmento {i}: "
            f"[bold]{format_duration(start_ms)}[/] → [bold]{format_duration(end_ms)}[/] "
            f"([dim]{format_duration(len(segment))}[/])"
        )

    combined.export(output, format="mp3", bitrate="192k")
    return len(combined)


@cli.command()
@click.argument("url")
@click.argument("segments", nargs=-1, required=True)
@click.option("-o", "--output", default=None, help="Nome do arquivo de saída (padrão: título do vídeo).")
@click.option("--force-download", is_flag=True, default=False, help="Forçar novo download mesmo se já existir em cache.")
def auto(url: str, segments: tuple[str, ...], output: str | None, force_download: bool):
    """Baixa do YouTube, aplica cortes e junta em um único comando.

    \b
    Se o vídeo já foi baixado antes, reutiliza o arquivo em cache
    (.cache/<video_id>.mp3) sem precisar baixar novamente.

    \b
    Cada segmento é definido como START-END:
      START e END: mm:ss, segundos ou 'end'

    \b
    Exemplos:
      python ytmp3.py auto "https://..." 0:00-1:54 3:00-end -o final.mp3
      python ytmp3.py auto "https://..." 0:00-1:00 2:00-3:30 5:00-end -o mix.mp3
      python ytmp3.py auto "https://..." 0:00-2:00 --force-download -o novo.mp3
    """
    # Validate segment format
    parsed_segments = []
    for seg in segments:
        if "-" not in seg:
            console.print(f"[red]Erro:[/] Formato inválido: '{seg}'. Use START-END (ex: 0:00-2:00).")
            sys.exit(1)
        parts = seg.split("-", 1)
        parsed_segments.append((parts[0], parts[1]))

    cache_file = _cache_path(url)

    # ── Step 1: Download (or use cache) ──────────
    console.rule("[bold]Passo 1/2: Download[/]")

    if cache_file and cache_file.exists() and not force_download:
        video_title = _load_title(url)
        if not video_title:
            # Title not cached yet — fetch without downloading
            try:
                video_title = get_video_title(url)
                _save_title(url, video_title)
            except Exception:
                video_title = cache_file.stem
        console.print(
            f"[green]✓[/] Usando cache: [bold]{cache_file.name}[/] "
            f"[dim](use --force-download para baixar novamente)[/]"
        )
        source_mp3 = str(cache_file)
    else:
        dest = str(cache_file) if cache_file else os.path.join(tempfile.gettempdir(), "ytmp3_full.mp3")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Baixando e convertendo...", total=None)
            video_title = download_audio(url, dest)
            progress.update(task, description=f"Baixado: {video_title}")
        _save_title(url, video_title)
        console.print(f"[green]✓[/] Download concluído: [bold]{video_title}[/]")
        source_mp3 = dest

    # Resolve output name: use video title if -o not given
    if output is None:
        output = _sanitize(video_title) + ".mp3"
    output = _out(output)

    console.print(Panel(
        f"[bold cyan]URL:[/] {url}\n"
        f"[bold cyan]Segmentos:[/] {', '.join(segments)}\n"
        f"[bold cyan]Saída:[/] {Path(output).name}",
        title="ytmp3 auto"
    ))

    # ── Step 2: Cut & Merge ───────────────────────
    console.rule("[bold]Passo 2/2: Cortes e Junção[/]")
    total_ms = _cut_and_merge(source_mp3, parsed_segments, output)

    console.print(
        f"\n[bold green]✓ Concluído![/] "
        f"[bold]{output}[/] "
        f"([dim]{format_duration(total_ms)}[/])"
    )


# ── TRANSCRIBE ────────────────────────────────

def _is_url(source: str) -> bool:
    return source.startswith("http://") or source.startswith("https://")


def _resolve_mp3_source(source: str) -> str:
    """Return local MP3 path for a file or YouTube URL (downloads/uses cache)."""
    if not _is_url(source):
        if not Path(source).exists():
            console.print(f"[red]Erro:[/] Arquivo não encontrado: {source}")
            sys.exit(1)
        return source

    # It's a URL — use cache or download
    cache_file = _cache_path(source)
    if cache_file and cache_file.exists():
        console.print(
            f"[green]✓[/] Usando cache: [bold]{cache_file.name}[/] "
            f"[dim](use --force-download para baixar novamente)[/]"
        )
        return str(cache_file)

    dest = str(cache_file) if cache_file else os.path.join(tempfile.gettempdir(), "ytmp3_full.mp3")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Baixando e convertendo...", total=None)
        title = download_audio(source, dest)
        _save_title(source, title)
        progress.update(task, description=f"Baixado: {title}")
    console.print(f"[green]✓[/] Download concluído: [bold]{title}[/]")
    return dest


@cli.command()
@click.argument("source")
@click.option("-o", "--output", default=None, help="Arquivo de saída .txt (padrão: mesmo nome do MP3).")
@click.option("-m", "--model", default="small",
              type=click.Choice(["tiny", "base", "small", "medium", "large"]),
              show_default=True, help="Modelo Whisper (tiny=rápido, large=preciso).")
@click.option("-l", "--language", default="pt", show_default=True,
              help="Idioma do áudio (pt, en, es, ...). 'auto' para detectar automaticamente.")
@click.option("--timestamps", is_flag=True, default=False,
              help="Incluir timestamps [HH:MM:SS] no texto.")
@click.option("--force-download", is_flag=True, default=False,
              help="Forçar novo download se SOURCE for uma URL.")
def transcribe(source: str, output: str | None, model: str, language: str, timestamps: bool, force_download: bool):
    """Transcreve áudio de um MP3 ou URL do YouTube para texto.

    \b
    SOURCE pode ser um arquivo MP3 local ou uma URL do YouTube.
    Se a URL já foi baixada antes, reutiliza o cache automaticamente.

    \b
    Modelos disponíveis (qualidade x velocidade):
      tiny   → mais rápido, menos preciso
      base   → rápido
      small  → bom equilíbrio (padrão)
      medium → mais preciso, mais lento
      large  → máxima precisão

    \b
    Exemplos:
      python ytmp3.py transcribe musica.mp3
      python ytmp3.py transcribe musica.mp3 -m medium --timestamps
      python ytmp3.py transcribe "https://youtube.com/watch?v=XYZ" -m large -l pt
    """
    try:
        import whisper
    except ImportError:
        console.print(
            "[red]Erro:[/] whisper não instalado.\n"
            "Instale com: [bold]pip install openai-whisper[/]"
        )
        sys.exit(1)

    console.print(Panel(
        f"[bold cyan]Fonte:[/]   {source}\n"
        f"[bold cyan]Modelo:[/]  {model}\n"
        f"[bold cyan]Idioma:[/]  {'auto-detectar' if language == 'auto' else language}",
        title="ytmp3 transcribe"
    ))

    # ── Step 1: Resolve MP3 ───────────────────────
    if _is_url(source) and force_download:
        cache_file = _cache_path(source)
        if cache_file and cache_file.exists():
            cache_file.unlink()

    mp3_path = _resolve_mp3_source(source)

    # ── Step 2: Determine output path ────────────
    if output is None:
        output = str(Path(mp3_path).with_suffix(".txt"))
    elif not output.endswith(".txt"):
        output = output + ".txt"

    # If output has no directory, put it beside the mp3
    if Path(output).parent == Path("."):
        output = str(Path(mp3_path).parent / Path(output).name)

    # ── Step 3: Load model ────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"Carregando modelo '{model}'...", total=None)
        whisper_model = whisper.load_model(model)
        progress.update(task, description=f"Modelo '{model}' carregado.")

    # ── Step 4: Transcribe ────────────────────────
    lang_arg = None if language == "auto" else language
    console.print(f"[dim]Transcrevendo [bold]{Path(mp3_path).name}[/] — isso pode demorar...[/]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Transcrevendo...", total=None)
        result = whisper_model.transcribe(mp3_path, language=lang_arg, verbose=False)
        progress.update(task, description="Transcrição concluída.")

    # ── Step 5: Save output ───────────────────────
    if timestamps:
        lines = []
        for seg in result["segments"]:
            start = format_duration(int(seg["start"] * 1000))
            lines.append(f"[{start}] {seg['text'].strip()}")
        text_out = "\n".join(lines)
    else:
        text_out = result["text"].strip()

    Path(output).write_text(text_out, encoding="utf-8")

    detected_lang = result.get("language", "?")
    word_count = len(text_out.split())
    console.print(
        f"\n[bold green]✓ Transcrição salva em[/] [bold]{output}[/]\n"
        f"  Idioma detectado: [bold]{detected_lang}[/] | "
        f"Palavras: [bold]{word_count:,}[/]"
    )


# ── INFO ──────────────────────────────────────

@cli.command()
@click.argument("file")
def info(file: str):
    """Exibe informações de um arquivo MP3.

    \b
    Exemplo:
      python ytmp3.py info musica.mp3
    """
    if not Path(file).exists():
        console.print(f"[red]Erro:[/] Arquivo não encontrado: {file}")
        sys.exit(1)

    audio = AudioSegment.from_mp3(file)
    size_mb = Path(file).stat().st_size / (1024 * 1024)

    console.print(Panel(
        f"[bold]Arquivo:[/]    {file}\n"
        f"[bold]Duração:[/]    {format_duration(len(audio))}\n"
        f"[bold]Canais:[/]     {audio.channels} ({'Stereo' if audio.channels == 2 else 'Mono'})\n"
        f"[bold]Sample rate:[/] {audio.frame_rate} Hz\n"
        f"[bold]Tamanho:[/]    {size_mb:.2f} MB",
        title="ytmp3 info"
    ))


if __name__ == "__main__":
    cli()
