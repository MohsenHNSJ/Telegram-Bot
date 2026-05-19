"""YouTube Downloader Service."""

import asyncio

from yt_dlp import YoutubeDL  # type: ignore[import-untyped]


async def download_youtube_video(url: str) -> str:
    """Download YouTube video and return the file path."""
    ydl_opts = {
        "format": "best[ext=mp4]/best",
        "outtmpl": "%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    def _download() -> str:
        with YoutubeDL(ydl_opts) as ydl:  # type: ignore[reportArgumentType]
            info = ydl.extract_info(url)
            return str(ydl.prepare_filename(info))

    file_path: str = await asyncio.to_thread(_download)
    return file_path
