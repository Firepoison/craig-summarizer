# Standard/Python imports
import json
import os
import sys
import tty
import termios
import re
from pathlib import Path

# 3rd party imports
import whisper
from mutagen import File as MutagenFile
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TimeElapsedColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich.markdown import Markdown

# Project imports
from src.summarizer import Summarizer

class WhisperProgressWriter:
    def __init__(self, progress, task_id):
        self.progress = progress
        self.task_id = task_id
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.pattern = re.compile(r"-->\s*(?:(\d+):)?(\d{2}):(\d{2})\.(\d{3})")

    def write(self, text):
        match = self.pattern.search(text)
        if match:
            h = int(match.group(1)) if match.group(1) else 0
            m = int(match.group(2))
            s = int(match.group(3))
            ms = int(match.group(4))
            current_time_sec = h * 3600 + m * 60 + s + ms / 1000.0
            self.progress.update(self.task_id, completed=current_time_sec)
        
        # We silently swallow ALL other output (including tqdm \r and warnings)
        # to ensure the rich progress bar remains pristine.

    def flush(self):
        pass

    def __enter__(self):
        sys.stdout = self
        sys.stderr = self
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr

def get_audio_files(directory_path="src/data/audio/"):
    """Scans the directory for audio files."""
    valid_extensions = {".flac", ".mp3", ".wav", ".m4a"}
    directory = Path(directory_path)
    
    if not directory.exists() or not directory.is_dir():
        return []
        
    return [
        file for file in directory.iterdir()
        if file.is_file() and file.suffix.lower() in valid_extensions
    ]

def get_duration_str(file_path):
    """Returns formatted duration string (HH:MM:SS) for an audio file."""
    try:
        audio = MutagenFile(file_path)
        if audio is not None and audio.info is not None:
            length = int(audio.info.length)
            hours, remainder = divmod(length, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"
    except Exception:
        pass
    return "Unknown"

def get_key():
    """Reads a single keypress from standard input."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def select_audio_file(audio_files, console):
    """Interactive scrolling menu using rich."""
    current_index = 0

    def generate_table():
        table = Table(title="[bold]Available Audio Files (Use Arrow Keys & Enter)[/bold]")
        table.add_column("No.", style="cyan", justify="right")
        table.add_column("Filename", style="magenta")
        table.add_column("Duration", style="yellow", justify="right")
        table.add_column("Size (MB)", justify="right")

        for idx, file in enumerate(audio_files):
            size_mb = file.stat().st_size / (1024 * 1024)
            duration_str = get_duration_str(str(file))
            style = "reverse" if idx == current_index else None
            table.add_row(
                str(idx + 1), 
                file.name, 
                duration_str, 
                f"{size_mb:.2f}",
                style=style
            )
        return table

    with Live(generate_table(), auto_refresh=False, console=console) as live:
        while True:
            key = get_key()
            if key == '\x1b[A': # Up
                current_index = max(0, current_index - 1)
            elif key == '\x1b[B': # Down
                current_index = min(len(audio_files) - 1, current_index + 1)
            elif key == '\r': # Enter
                return audio_files[current_index]
            elif key == '\x03': # Ctrl-C
                return None
            
            live.update(generate_table(), refresh=True)

def handle_transcription(selected_file, console):
    audiofile_path = str(selected_file)
    transcription_dir = Path("src/data/transcriptions")
    transcription_dir.mkdir(parents=True, exist_ok=True)
    transcription_out_path = transcription_dir / f"{selected_file.stem}.json"
    
    if transcription_out_path.exists():
        console.print(f"[cyan]Found existing transcription. Loading from {transcription_out_path}...[/cyan]")
        with open(transcription_out_path, "r") as f:
            return json.load(f)

    try:
        audio_info = MutagenFile(audiofile_path)
        total_sec = audio_info.info.length if audio_info and audio_info.info else 100
    except Exception:
        total_sec = 100

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task1 = progress.add_task("[cyan]Loading Whisper model (small)...", total=total_sec)
        transcriber = whisper.load_model("small")
        
        progress.update(task1, description=f"[cyan]Transcribing {selected_file.name}...", completed=0)
        
        with WhisperProgressWriter(progress, task1):
            transcription = transcriber.transcribe(audiofile_path, verbose=True)
            
        progress.update(task1, description="[green]Transcription complete!", completed=total_sec)

    with open(transcription_out_path, "w") as f:
        json.dump(transcription, f, indent=4)
    console.print(f"[dim]Saved transcription data to {transcription_out_path}[/dim]")
    return transcription

def handle_summarization(transcription, selected_file, console):
    console.print("\n[bold magenta]Initializing Summarizer...[/bold magenta]")
    summarizer = Summarizer()
    
    summary_text = ""
    panel = Panel(Markdown(summary_text), title="Gemini Summary (Streaming...)", border_style="magenta")
    
    with Live(panel, console=console, refresh_per_second=8) as live:
        for chunk in summarizer.summarize_stream(transcription=transcription.get("text")):
            summary_text += chunk
            live.update(Panel(Markdown(summary_text), title="Gemini Summary (Streaming...)", border_style="magenta"))
            
        live.update(Panel(Markdown(summary_text), title="Gemini Summary (Complete)", border_style="green"))

    summary_dir = Path("src/data/summaries")
    summary_dir.mkdir(parents=True, exist_ok=True)
    summary_out_path = summary_dir / f"{selected_file.stem}.txt"
    
    with open(summary_out_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    
    console.print(f"\n[dim]Saved summary to {summary_out_path}[/dim]")

def main():
    # Force rich to use the underlying un-monkey-patchable stdout
    console = Console(file=sys.__stdout__)
    console.print(Panel.fit("[bold blue]Craig Summarizer[/bold blue]", border_style="blue"))
    
    # 1. File Selection
    audio_files = sorted(get_audio_files())
    if not audio_files:
        console.print("[red]No audio files found in src/data.[/red]")
        return

    selected_file = select_audio_file(audio_files, console)
    if not selected_file:
        console.print("\n[yellow]Operation cancelled.[/yellow]")
        return
        
    console.print(f"\n[green]Selected:[/green] {selected_file.name}")

    # 2. Transcription
    transcription = handle_transcription(selected_file, console)
    
    # 3. Summarization
    handle_summarization(transcription, selected_file, console)

    console.print("\n[bold green]Process Completed Successfully![/bold green]")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(130)

