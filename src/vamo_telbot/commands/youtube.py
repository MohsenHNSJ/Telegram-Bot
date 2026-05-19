"""YouTube video downloader command handler for the Telegram bot."""

# pylint: disable=W0718
import asyncio
from pathlib import Path

from telethon import events  # type: ignore[import-untyped]

from vamo_telbot.services.youtube_downloader import download_youtube_video


async def handle_youtube_download(event: events.newmessage.NewMessage.Event) -> None:
    """Handle incoming YouTube links and trigger the download process.

    Args:
        event (events.newmessage.NewMessage.Event): The event triggered by a new message,
        containing a YouTube link.
    """
    url: str = event.message.message
    await event.reply("⏳ Downloading your YouTube video...")

    try:
        file_path: str = await download_youtube_video(url)
        await event.reply("✅ Download finished! Sending video...")

        await event.client.send_file(  # pyright: ignore[reportOptionalMemberAccess]
            event.chat_id,
            file_path,
            caption="Downloaded from YouTube 🎬",
        )

        # Clean up the downloaded file after sending
        await asyncio.to_thread(Path(file_path).unlink)

    except Exception as e:  # noqa: BLE001
        await event.reply(f"❌ Failed to download video: {e!s}")
