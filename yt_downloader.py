#!/usr/bin/env python3
# Single-URL YouTube downloader (mp3 or HD/4K video only), hardened for safe filenames & paths.

import os
import re
import sys
from typing import Dict, Any, Optional

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table

console = Console()

def safe_join(base: str, *paths: str) -> str:
    """Join paths and ensure the result stays within base (prevent traversal)."""
    base_abs = os.path.abspath(base)
    joined = os.path.abspath(os.path.join(base_abs, *paths))
    if os.path.commonpath([base_abs, joined]) != base_abs:
        raise ValueError(f"Unsafe output path resolved outside base: {joined}")
    return joined

def natural_size(num: float) -> str:
    for unit in ['B','KB','MB','GB','TB']:
        if abs(num) < 1024.0:
            return "%3.1f %s" % (num, unit)
        num /= 1024.0
    return "%.1f PB" % num

def valid_youtube_url(s: str) -> bool:
    return bool(re.search(r'^(https?://)?(www\.)?(youtube\.com|youtu\.be)/', s))

def ensure_folder(folder: str) -> str:
    try:
        os.makedirs(folder, exist_ok=True)
    except OSError as e:
        console.print(f"[red]Failed to create output folder:[/red] {e}")
        sys.exit(1)
    return os.path.abspath(folder)

def _infer_height_from_info(info: Dict[str, Any]) -> Optional[int]:
    h = info.get("height")
    if isinstance(h, int):
        return h
    res = info.get("resolution")
    if isinstance(res, str) and "x" in res:
        try:
            return int(res.split("x")[-1])
        except ValueError:
            return None
    return None

def download_one(url: str, fmt: str, outdir: str) -> Optional[str]:
    """
    Download a single URL as mp3 or HD/4K video using yt-dlp with hardened filename behavior.
    Returns final file path or None on failure.
    """
    try:
        from yt_dlp import YoutubeDL
    except Exception:
        console.print("[red]yt-dlp is not installed. Install with: pip install yt-dlp[/red]")
        return None

    # Save directly under chosen folder
    outtmpl = safe_join(outdir, "%(title)s.%(ext)s")

    # Base safe options
    opts: Dict[str, Any] = {
        "restrictfilenames": True,   # POSIX-safe ASCII filenames
        "windowsfilenames": True,    # avoid reserved chars on Windows
        "nocheckcertificate": False, # explicit TLS verification
        "outtmpl": outtmpl,
        "noplaylist": True,          # ensure single item only
    }

    if fmt == "mp3":
        opts.update(dict(
            format="bestaudio/best",
            extractaudio=True,
            audioformat="mp3",
            postprocessors=[{"key": "FFmpegExtractAudio", "preferredcodec": "mp3"}],
        ))
    elif fmt == "mp4":
        # Only HD/4K: try 2160p -> 1440p -> 1080p -> 720p. No SD fallback.
        # Use MKV to support AV1/VP9 without re-encode. Change to "mp4" if you must.
        opts.update({
            "format": (
                "bestvideo[height=2160]+bestaudio/"
                "bestvideo[height=1440]+bestaudio/"
                "bestvideo[height=1080]+bestaudio/"
                "bestvideo[height=720]+bestaudio"
            ),
            "merge_output_format": "mkv",
        })
    else:
        console.print("[red]Unsupported format. Choose mp3 or mp4.[/red]")
        return None

    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)

            # Normalize to the actual downloaded item if yt-dlp returns a parent dict
            if "requested_downloads" in info and info["requested_downloads"]:
                # Often contains separate video/audio entries; pick the first file path present
                for rd in info["requested_downloads"]:
                    fp = rd.get("filepath")
                    if fp and os.path.exists(fp):
                        final_path = fp
                        height = _infer_height_from_info(rd)
                        break
                else:
                    final_path = info.get("filepath")
                    height = _infer_height_from_info(info)
            else:
                final_path = info.get("filepath")
                height = _infer_height_from_info(info)

            # Enforce HD/4K guarantee (≥720p) for video path
            if fmt == "mp4":
                if height is None or height < 720:
                    console.print("[red]No HD/4K stream found (>=720p).[/red]")
                    return None

            if final_path and os.path.exists(final_path):
                size = os.path.getsize(final_path)
                t = Table(title="Download Summary")
                t.add_column("File")
                if fmt == "mp4":
                    t.add_column("Resolution", justify="center")
                t.add_column("Size", justify="right")
                if fmt == "mp4":
                    t.add_row(os.path.basename(final_path), f"{height}p" if height else "—", natural_size(size))
                else:
                    t.add_row(os.path.basename(final_path), natural_size(size))
                console.print(t)
                return final_path
            else:
                console.print("[yellow]Download finished but final file path was not reported.[/yellow]")
                return None
    except Exception as e:
        console.print(f"[red]Download failed:[/red] {e}")
        return None

def main():
    console.print("[bold]Single URL YouTube Downloader (HD/4K only for video)[/bold]")

    # 1) Paste URL
    url = Prompt.ask("Paste the YouTube URL").strip()
    if not url or not valid_youtube_url(url):
        console.print("[red]Please paste a valid YouTube or youtu.be URL.[/red]")
        sys.exit(1)

    # 2) Choose format
    fmt = Prompt.ask("Choose format", choices=["mp3", "mp4"], default="mp3")

    # 3) Choose output folder
    default_out = "Downloads"
    # outdir_in = Prompt.ask("Type 'Downloads' as Output Fodler", default=default_out).strip() or default_out
    outdir_in = default_out
    outdir = ensure_folder(outdir_in)

    # 4) Confirm and download
    console.print(f"\nURL: [blue]{url}[/blue]")
    console.print(f"Format: [bold]{fmt}[/bold]")
    console.print(f"Folder: [green]{outdir}[/green]\n")
    if not Confirm.ask("Start download?", default=True):
        console.print("Cancelled.")
        sys.exit(0)

    final_path = download_one(url, fmt, outdir)
    if final_path:
        console.print(f"[green]Done:[/green] {final_path}")
        if Confirm.ask("Open download folder?", default=False):
            try:
                if sys.platform == "win32":
                    os.startfile(outdir)  # type: ignore[attr-defined]
                elif sys.platform == "darwin":
                    import subprocess
                    subprocess.run(["open", outdir], check=False)
                else:
                    import subprocess
                    subprocess.run(["xdg-open", outdir], check=False)
            except Exception as e:
                console.print(f"[yellow]Could not open folder:[/yellow] {e}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[red]Exiting...[/red]")
        sys.exit(0)