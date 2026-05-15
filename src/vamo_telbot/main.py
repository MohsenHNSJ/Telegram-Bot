"""Main module of Telegram Bot"""

# pylint: disable=W0611,C0115,C0103,R0205,C0116,R0915,C0301,W1406,W0201,C0302,C0325,E0102,W0718,W0719,W0706,W0707,C0104
# ruff: noqa: ANN201,PLR0915, ERA001, E501, PLR2004, C901, PLR0912, EXE002, D103, PTH122, PTH118, PTH110, ANN002, ASYNC109, SIM105, S110, BLE001, TRY301, TRY002, TRY003, RSE102, EM102, ASYNC240, PTH107, B904, D415, PTH208, ANN202, EM101, PTH204, PLR0913, RUF001, RUF013, PTH119, PTH202, SIM102, RUF003, PLR1714, PIE810
# mypy: ignore-errors
# type: ignore[all]
# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownMemberType=false
# pyright: reportPrivateImportUsage=false
# pyright: reportUnknownVariableType=false
# pyright: reportRedeclaration=false
# pyright: reportPossiblyUnboundVariable=false
# pyright: reportAttributeAccessIssue=false
# pyright: reportOptionalMemberAccess=false
# pyright: reportArgumentType=false
# region Imports
import asyncio
import os
import re
import time

import aiofiles
import aiohttp
from telethon import TelegramClient, events
from telethon.tl.custom import Button, Message

from vamo_telbot.commands.start import handle_start
from vamo_telbot.config.telegram import (
    load_api_hash,
    load_api_id,
    load_bot_token,
    save_api_hash,
    save_api_id,
    save_bot_token,
)
from vamo_telbot.global_constants import AUTHORIZED_USER_ID, SECOND_USER_ID
from vamo_telbot.utils import is_adult_url, is_social_url, is_youtube_url, make_bar

# endregion Imports

# ==================== تنظیمات ====================
SESSION_NAME: str = "telegram_bot"
DRIVE_PATH = "drive:/TelegramUploads"
DOWNLOAD_DIR = "downloads"
COOKIES_FILE = "/root/cookies.txt"
INSTAGRAM_COOKIES = "/root/instagram_cookies.txt"

USER_FOLDERS = {
    AUTHORIZED_USER_ID: "USER1",
    SECOND_USER_ID: "USER2",
}

# os.makedirs(DOWNLOAD_DIR, exist_ok=True)

telegram_bot: TelegramClient = TelegramClient(
    SESSION_NAME,
    1,
    "NOT_SET",
)

# ==================== Queue & Cancel ====================
_download_queue = asyncio.Queue()
_cancel_flags = {}
_active_tasks = {}


# ==================== تشخیص URL ====================
def unique_filepath(name: str) -> str:
    base, ext = os.path.splitext(name)
    ts = int(time.time())
    candidate = os.path.join(DOWNLOAD_DIR, f"{base}_{ts}{ext}")
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(DOWNLOAD_DIR, f"{base}_{ts}_{counter}{ext}")
        counter += 1
    return candidate


# ==================== rclone async ====================
async def run_rclone_async(*args, timeout: float = 60):
    try:
        process = await asyncio.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
    except TimeoutError:
        try:
            process.kill()
        except Exception:
            pass

        class Result:
            pass

        r = Result()
        r.returncode = -1
        r.stdout = ""
        r.stderr = "خطا: timeout — rclone پاسخ نداد"
        return r

    class Result:
        pass

    r = Result()
    r.returncode = process.returncode
    r.stdout = stdout.decode("utf-8", errors="ignore")
    r.stderr = stderr.decode("utf-8", errors="ignore")
    return r


# ==================== توابع دانلود ====================
async def download_from_url(
    url: str,
    filename: str,
    status_msg: Message | None = None,
    cancel_event: asyncio.Event | None = None,
):
    local_path = unique_filepath(filename)
    try:
        async with aiohttp.ClientSession() as session, session.get(url) as response:
            if response.status != 200:
                raise Exception(f"HTTP {response.status}")
            total = int(response.headers.get("Content-Length", 0))
            downloaded = 0
            last_update = 0
            async with aiofiles.open(local_path, "wb") as f:
                async for chunk in response.content.iter_chunked(512 * 1024):
                    if cancel_event and cancel_event.is_set():
                        raise asyncio.CancelledError()
                    await f.write(chunk)
                    downloaded += len(chunk)
                    now = time.time()
                    if status_msg and total and (now - last_update) >= 3:
                        pct = downloaded / total * 100
                        bar = make_bar(pct)
                        dl_mb = downloaded / (1024 * 1024)
                        tot_mb = total / (1024 * 1024)
                        try:
                            await status_msg.edit(
                                f"📥 در حال دانلود...\n"
                                f"{bar} {pct:.0f}%\n"
                                f"💾 {dl_mb:.1f} / {tot_mb:.1f} MB",
                            )
                        except Exception:
                            pass
                        last_update = now
            return local_path
    except asyncio.CancelledError:
        if os.path.exists(local_path):
            os.remove(local_path)
        raise
    except Exception as e:
        if os.path.exists(local_path):
            os.remove(local_path)
        raise Exception(f"خطا در دانلود: {e!s}")


async def download_yt_dlp(
    cmd: list,
    file_exts: tuple,
    status_msg: Message | None = None,
    cancel_event: asyncio.Event | None = None,
):
    """اجرای yt-dlp با نمایش progress و پشتیبانی از کنسل"""
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    last_update = 0
    stderr_buf = b""
    all_stderr_lines = []

    async def read_stderr():
        nonlocal stderr_buf, all_stderr_lines, last_update
        while True:
            chunk = await process.stderr.read(512)
            if not chunk:
                break
            stderr_buf += chunk
            parts = re.split(rb"[\r\n]", stderr_buf)
            stderr_buf = parts[-1]
            for raw_line in parts[:-1]:
                decoded = raw_line.decode("utf-8", errors="ignore").strip()
                if not decoded:
                    continue
                all_stderr_lines.append(decoded)
                if status_msg and "[download]" in decoded:
                    m = re.search(
                        r"(\d+\.?\d*)%\s+of\s+~?([\d.]+)(MiB|GiB|KiB)",
                        decoded,
                    )
                    if m:
                        now = time.time()
                        if now - last_update >= 3:
                            pct = float(m.group(1))
                            size_val = float(m.group(2))
                            size_unit = m.group(3)
                            bar = make_bar(pct)
                            try:
                                await status_msg.edit(
                                    f"📥 در حال دانلود...\n"
                                    f"{bar} {pct:.0f}%\n"
                                    f"💾 {size_val:.1f} {size_unit}",
                                )
                            except Exception:
                                pass
                            last_update = now

    stderr_task = asyncio.create_task(read_stderr())

    while process.returncode is None:
        if cancel_event and cancel_event.is_set():
            process.kill()
            await process.wait()
            stderr_task.cancel()
            raise asyncio.CancelledError()
        try:
            await asyncio.wait_for(process.wait(), timeout=1.0)
        except TimeoutError:
            pass

    await stderr_task
    if stderr_buf:
        all_stderr_lines.append(
            stderr_buf.decode(
                "utf-8",
                errors="ignore",
            ).strip(),
        )

    if process.returncode != 0:
        raise Exception("\n".join(all_stderr_lines)[-600:])

    files = [f for f in os.listdir(DOWNLOAD_DIR) if f.endswith(file_exts)]
    if not files:
        raise Exception("فایل دانلود‌شده پیدا نشد")
    latest = max(
        files,
        key=lambda x: os.path.getmtime(
            os.path.join(DOWNLOAD_DIR, x),
        ),
    )
    return os.path.join(DOWNLOAD_DIR, latest)


async def download_youtube(
    url: str,
    quality: str = "480",
    bitrate: str = None,
    status_msg: Message | None = None,
    cancel_event: asyncio.Event | None = None,
):
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    if quality == "audio":
        if bitrate == "128":
            format_spec = "bestaudio[abr<=128]/bestaudio"
            audio_quality = "128K"
        elif bitrate == "320":
            format_spec = "bestaudio[abr<=320]/bestaudio"
            audio_quality = "320K"
        else:
            format_spec = "bestaudio[abr<=64]/bestaudio"
            audio_quality = "64K"
        cmd = [
            "yt-dlp",
            "--cookies",
            COOKIES_FILE,
            "-f",
            format_spec,
            "-o",
            output_template,
            "--extract-audio",
            "--audio-format",
            "mp3",
            "--audio-quality",
            audio_quality,
            "--no-playlist",
            "--newline",
            "--sleep-interval",
            "3",
            "--max-sleep-interval",
            "5",
            "--limit-rate",
            "5M",
            url,
        ]
        file_exts = (".mp3",)
    else:
        format_spec = f"best[height<={quality}]"
        cmd = [
            "yt-dlp",
            "--cookies",
            COOKIES_FILE,
            "-f",
            format_spec,
            "-o",
            output_template,
            "--no-playlist",
            "--newline",
            "--sleep-interval",
            "3",
            "--max-sleep-interval",
            "5",
            "--limit-rate",
            "5M",
            url,
        ]
        file_exts = (".mp4", ".mkv", ".webm")
    try:
        return await download_yt_dlp(cmd, file_exts, status_msg, cancel_event)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        raise Exception(f"خطا در دانلود یوتیوب: {e!s}")


async def download_adult_site(
    url: str,
    quality: str,
    status_msg: Message | None = None,
    cancel_event: asyncio.Event | None = None,
):
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    format_spec = f"best[height<={quality}]/best"
    cmd = [
        "yt-dlp",
        "--cookies",
        COOKIES_FILE,
        "-f",
        format_spec,
        "-o",
        output_template,
        "--no-playlist",
        "--no-warnings",
        "--newline",
        "--sleep-interval",
        "3",
        "--max-sleep-interval",
        "6",
        "--extractor-retries",
        "3",
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "--add-header",
        "Accept-Language:en-US,en;q=0.9",
        "--add-header",
        "Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "--add-header",
        "Referer:https://spankbang.com/",
        url,
    ]
    try:
        return await download_yt_dlp(cmd, (".mp4", ".mkv", ".webm"), status_msg, cancel_event)
    except asyncio.CancelledError:
        raise
    except Exception as e:
        raise Exception(f"خطا در دانلود: {e!s}")


async def download_social(
    url: str,
    status_msg: Message | None = None,
    cancel_event: asyncio.Event | None = None,
):
    output_template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
    cookies_file = INSTAGRAM_COOKIES if "instagram" in url.lower() else COOKIES_FILE
    cmd = [
        "yt-dlp",
        "--cookies",
        cookies_file,
        "--user-agent",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-f",
        "bestvideo+bestaudio/best",
        "-o",
        output_template,
        "--no-playlist",
        "--no-warnings",
        "--newline",
        "--sleep-interval",
        "4",
        "--max-sleep-interval",
        "10",
        url,
    ]
    try:
        return await download_yt_dlp(
            cmd,
            (".mp4", ".mkv", ".webm", ".mov"),
            status_msg,
            cancel_event,
        )
    except asyncio.CancelledError:
        raise
    except Exception as e:
        stderr_text = str(e).lower()
        if "instagram" in url.lower() and (
            "login required" in stderr_text or "cookies" in stderr_text
        ):
            raise Exception(
                "اینستاگرام نیاز به کوکی معتبر دارد.\nفایل instagram_cookies.txt را بررسی کنید.",
            )
        raise Exception(f"خطا در دانلود شبکه‌های اجتماعی: {e!s}")


# ==================== آپلود ====================
async def upload_to_drive(
    file_path: str,
    status_msg: Message | None,
    file_name: str,
    original_msg: Message | None = None,
    user_id: int | None = None,
    cancel_event: asyncio.Event | None = None,
):
    user_folder = USER_FOLDERS.get(user_id, "") if user_id else ""
    dest_path = f"{DRIVE_PATH}/{user_folder}" if user_folder else DRIVE_PATH

    try:
        try:
            await status_msg.edit(
                f"📤 در حال آپلود به Google Drive...\n"
                f"📁 {file_name}\n"
                f"👤 پوشه: {user_folder or 'پیش‌فرض'}",
            )
        except Exception:
            if original_msg:
                status_msg = await original_msg.reply(f"📤 در حال آپلود...\n📁 {file_name}")

        rclone_cmd = [
            "rclone",
            "copy",
            "--progress",
            file_path,
            f"{dest_path}/",
        ]
        process = await asyncio.create_subprocess_exec(
            *rclone_cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        last_update = 0
        rclone_buf = b""

        async def read_rclone_progress():
            nonlocal last_update, rclone_buf
            while True:
                chunk = await process.stderr.read(512)
                if not chunk:
                    break
                rclone_buf += chunk
                parts = re.split(rb"[\r\n]", rclone_buf)
                rclone_buf = parts[-1]
                for raw_line in parts[:-1]:
                    decoded = raw_line.decode("utf-8", errors="ignore")
                    m = re.search(r"Transferred:.*?([\d.]+)%", decoded)
                    if m:
                        now = time.time()
                        if now - last_update >= 3:
                            pct = float(m.group(1))
                            bar = make_bar(pct)
                            try:
                                await status_msg.edit(
                                    f"📤 در حال آپلود...\n{bar} {pct:.0f}%\n📁 {file_name}",
                                )
                            except Exception:
                                pass
                            last_update = now

        progress_task = asyncio.create_task(read_rclone_progress())

        while process.returncode is None:
            if cancel_event and cancel_event.is_set():
                process.kill()
                await process.wait()
                progress_task.cancel()
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise asyncio.CancelledError()
            try:
                await asyncio.wait_for(process.wait(), timeout=1.0)
            except TimeoutError:
                pass

        await progress_task

        if os.path.exists(file_path):
            os.remove(file_path)

        if process.returncode == 0:
            link_result = await run_rclone_async("rclone", "link", f"{dest_path}/{file_name}")
            share_link = (
                link_result.stdout.strip()
                if link_result.returncode == 0
                else "لینک عمومی در دسترس نیست"
            )
            try:
                await status_msg.edit(
                    f"🎉 آپلود با موفقیت انجام شد!\n"
                    f"📁 {file_name}\n"
                    f"👤 پوشه: {user_folder or 'پیش‌فرض'}\n\n"
                    f"🔗 لینک اشتراک:\n{share_link}",
                )
            except Exception:
                if original_msg:
                    await original_msg.reply(
                        f"🎉 آپلود با موفقیت انجام شد!\n📁 {file_name}\n\n🔗 {share_link}",
                    )
        else:
            stderr_out = (await process.stderr.read()).decode("utf-8", errors="ignore")
            raise Exception(stderr_out[:300])

    except asyncio.CancelledError:
        raise
    except Exception as e:
        msg_text = f"❌ خطا در آپلود: {e!s}"
        try:
            await status_msg.edit(msg_text)
        except Exception:
            if original_msg:
                await original_msg.reply(msg_text)


# ==================== Queue Worker ====================
async def queue_worker():
    while True:
        item = await _download_queue.get()
        user_id = item["user_id"]
        status_msg = item["status_msg"]
        original_msg = item["original_msg"]
        cancel_event = item.get("cancel_event")
        queue_pos = item.get("queue_pos", 0)

        try:
            job_type = item["type"]

            if queue_pos > 1:
                try:
                    await status_msg.edit(
                        f"⏳ در صف انتظار — موقعیت: {queue_pos}\n\nبرای لغو: /cancel",
                    )
                except Exception:
                    pass

            try:
                await status_msg.edit("🔄 شروع پردازش...\n\nبرای لغو: /cancel")
            except Exception:
                pass

            if job_type == "telegram_file":
                msg = item["msg"]
                file_name = item["file_name"]
                file_path: str = unique_filepath(file_name)
                size_mb = item["size_mb"]
                try:
                    await status_msg.edit(
                        f"📥 در حال دریافت فایل تلگرام...\n💾 {size_mb:.1f} MB\n\nبرای لغو: /cancel",
                    )
                except Exception:
                    pass
                if cancel_event and cancel_event.is_set():
                    raise asyncio.CancelledError()
                await msg.download_media(file_path)
                if cancel_event and cancel_event.is_set():
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    raise asyncio.CancelledError()
                try:
                    await status_msg.edit(f"✅ دریافت کامل!\n📁 {file_name}\n\n📤 در حال آپلود...")
                except Exception:
                    pass
                await upload_to_drive(
                    file_path,
                    status_msg,
                    os.path.basename(file_path),
                    original_msg=original_msg,
                    user_id=user_id,
                    cancel_event=cancel_event,
                )

            elif job_type == "direct_url":
                url = item["url"]
                filename = item["filename"]
                file_path = await download_from_url(url, filename, status_msg, cancel_event)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                try:
                    await status_msg.edit(
                        f"✅ دانلود کامل!\n📁 {filename}\n💾 {size_mb:.1f} MB\n\n📤 در حال آپلود...",
                    )
                except Exception:
                    pass
                await upload_to_drive(
                    file_path,
                    status_msg,
                    filename,
                    original_msg=original_msg,
                    user_id=user_id,
                    cancel_event=cancel_event,
                )

            elif job_type == "youtube":
                url = item["url"]
                quality = item["quality"]
                bitrate = item.get("bitrate")
                file_path = await download_youtube(url, quality, bitrate, status_msg, cancel_event)
                file_name = os.path.basename(file_path)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                try:
                    await status_msg.edit(
                        f"✅ دانلود کامل!\n📁 {file_name}\n💾 {size_mb:.1f} MB\n\n📤 در حال آپلود...",
                    )
                except Exception:
                    pass
                await upload_to_drive(
                    file_path,
                    status_msg,
                    file_name,
                    original_msg=original_msg,
                    user_id=user_id,
                    cancel_event=cancel_event,
                )

            elif job_type == "adult":
                url = item["url"]
                quality = item["quality"]
                file_path = await download_adult_site(url, quality, status_msg, cancel_event)
                file_name = os.path.basename(file_path)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                try:
                    await status_msg.edit(
                        f"✅ دانلود کامل!\n📁 {file_name}\n💾 {size_mb:.1f} MB\n\n📤 در حال آپلود...",
                    )
                except Exception:
                    pass
                await upload_to_drive(
                    file_path,
                    status_msg,
                    file_name,
                    original_msg=original_msg,
                    user_id=user_id,
                    cancel_event=cancel_event,
                )

            elif job_type == "social":
                url = item["url"]
                file_path = await download_social(url, status_msg, cancel_event)
                file_name = os.path.basename(file_path)
                size_mb = os.path.getsize(file_path) / (1024 * 1024)
                try:
                    await status_msg.edit(
                        f"✅ دانلود کامل!\n📁 {file_name}\n💾 {size_mb:.1f} MB\n\n📤 در حال آپلود...",
                    )
                except Exception:
                    pass
                await upload_to_drive(
                    file_path,
                    status_msg,
                    file_name,
                    original_msg=original_msg,
                    user_id=user_id,
                    cancel_event=cancel_event,
                )

        except asyncio.CancelledError:
            try:
                await status_msg.edit("🚫 عملیات لغو شد.")
            except Exception:
                pass
        except Exception as e:
            try:
                await status_msg.edit(f"❌ خطا: {e!s}")
            except Exception:
                pass
        finally:
            _cancel_flags.pop(user_id, None)
            _active_tasks.pop(user_id, None)
            _download_queue.task_done()


def enqueue(item: dict):
    pos = _download_queue.qsize() + 1
    item["queue_pos"] = pos
    _download_queue.put_nowait(item)
    return pos


# ==================== /cancel ====================
@telegram_bot.on(events.NewMessage(pattern="/cancel"))
async def cancel_download(event: Message):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    uid = event.sender_id
    if uid in _cancel_flags:
        _cancel_flags[uid].set()
        await event.reply("🚫 درخواست لغو ارسال شد. لطفاً چند لحظه صبر کنید...")
    else:
        await event.reply("ℹ️ در حال حاضر هیچ عملیاتی در جریان نیست.")


# ==================== مدیریت فایل‌ها ====================
@telegram_bot.on(events.NewMessage(pattern="/file"))
async def file_manager(event: Message):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    user_id = event.sender_id
    user_folder = USER_FOLDERS.get(user_id, "Unknown")
    full_path = f"{DRIVE_PATH}/{user_folder}"

    msg = await event.reply(f"📂 در حال دریافت فایل‌های شما ({user_folder})...")

    result = await run_rclone_async("rclone", "ls", full_path, timeout=30)
    if result.returncode != 0 and result.returncode != -1:
        # rclone exit 3 = پوشه وجود نداره — طبیعی است
        if result.returncode != 3:
            await msg.edit(f"❌ خطا در دریافت فایل‌ها:\n{result.stderr[:300]}")
            return
    lines = [line.strip() for line in result.stdout.strip().split("\n") if line.strip()]

    if not lines:
        await msg.edit("📁 پوشه شما خالی است یا هنوز ساخته نشده.")
        return

    text = f"📁 **فایل‌های شما ({user_folder}):**\n\n"
    buttons = []
    for line in lines[:15]:
        parts = line.split()
        if len(parts) >= 2:
            filename = " ".join(parts[1:])
            buttons.append(
                [Button.inline(filename[:50], f"file_action:{filename}")],
            )

    if len(lines) > 15:
        text += f"... و {len(lines) - 15} فایل دیگر"

    await msg.edit(text, buttons=buttons)


@telegram_bot.on(events.CallbackQuery(pattern=re.compile(b"file_action:(.+)")))
async def file_action(event: events.CallbackQuery):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    filename = event.data.decode().split(":", 1)[1]
    buttons = [
        [Button.inline("🔄 تغییر نام", f"rename:{filename}")],
        [Button.inline("🗑 حذف", f"delete_confirm:{filename}")],
        [Button.inline("↩️ بازگشت", b"back_to_filelist")],
    ]
    await event.edit(
        f"📄 فایل انتخاب شده:\n`{filename}`\n\nچه کاری می‌خواهید انجام دهید؟",
        buttons=buttons,
    )


@telegram_bot.on(events.CallbackQuery(pattern=re.compile(b"delete_confirm:(.+)")))
async def delete_confirm(event: events.CallbackQuery):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    filename = event.data.decode().split(":", 1)[1]
    buttons = [
        [Button.inline("✅ بله، حذف شود", f"delete_do:{filename}")],
        [Button.inline("❌ انصراف", f"file_action:{filename}")],
    ]
    await event.edit(f"⚠️ آیا مطمئن هستید؟\n\n`{filename}`", buttons=buttons)


@telegram_bot.on(events.CallbackQuery(pattern=re.compile(b"delete_do:(.+)")))
async def delete_do(event: events.CallbackQuery):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    user_id = event.sender_id
    user_folder = USER_FOLDERS.get(user_id, "")
    filename = event.data.decode().split(":", 1)[1]
    full_path = f"{DRIVE_PATH}/{user_folder}/{filename}"
    await event.edit("🗑 در حال حذف...")
    result = await run_rclone_async("rclone", "deletefile", full_path)
    if result.returncode == 0:
        await event.edit(f"✅ فایل `{filename}` حذف شد.")
    else:
        await event.edit(f"❌ خطا در حذف:\n{result.stderr[:300]}")


@telegram_bot.on(events.CallbackQuery(pattern=re.compile(b"rename:(.+)")))
async def rename_start(event: events.CallbackQuery):
    if event.Event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    filename = event.data.decode().split(":", 1)[1]
    if not hasattr(telegram_bot, "rename_data"):
        telegram_bot.rename_data = {}
    telegram_bot.rename_data[event.Event.sender_id] = filename
    await event.edit(
        f"✏️ نام جدید برای فایل را بفرستید:\n`{filename}`\n\n(برای انصراف /cancel_rename بفرستید)",
    )


@telegram_bot.on(events.NewMessage(pattern="/cancel_rename"))
async def cancel_rename(event: events.NewMessage):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    if hasattr(telegram_bot, "rename_data") and event.sender_id in telegram_bot.rename_data:
        del telegram_bot.rename_data[event.sender_id]
        await event.reply("❌ تغییر نام لغو شد.")
    else:
        await event.reply("ℹ️ عملیات تغییر نام در جریان نیست.")


@telegram_bot.on(events.CallbackQuery(pattern=b"back_to_filelist"))
async def back_to_filelist(event: events.CallbackQuery):
    if event.Event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        return
    await file_manager(event)


@telegram_bot.on(events.NewMessage(pattern="/start"))
async def start(event: events.newmessage.NewMessage.Event) -> None:
    await handle_start(event)


# ==================== هندلر اصلی لینک ====================
@telegram_bot.on(events.NewMessage(pattern=r"^https?://"))
async def handle_url(event: events.NewMessage):
    if event.sender_id not in [AUTHORIZED_USER_ID, SECOND_USER_ID]:
        await event.reply("❌ شما دسترسی به این ربات ندارید.")
        return
    url = event.message.text.strip()
    msg: Message | None = await event.reply("🔍 در حال بررسی لینک...")

    if is_youtube_url(url):
        buttons = [
            [
                Button.inline("🎬 480p", b"yt_480"),
                Button.inline("🎬 720p", b"yt_720"),
            ],
            [
                Button.inline("🎬 1080p", b"yt_1080"),
                Button.inline("🎵 فقط صوتی", b"yt_audio_first"),
            ],
            [Button.inline("❌ انصراف", b"yt_cancel")],
        ]
        await msg.edit(
            "🎬 لینک **یوتیوب** شناسایی شد!\n\nکیفیت مورد نظر را انتخاب کنید:",
            buttons=buttons,
        )
        if not hasattr(telegram_bot, "temp_data"):
            telegram_bot.temp_data = {}
        telegram_bot.temp_data[event.sender_id] = {
            "url": url,
            "step": "quality",
            "type": "youtube",
            "status_msg": msg,
            "original_msg": event,
        }

    elif is_adult_url(url):
        buttons = [
            [
                Button.inline("🎬 360p", b"adult_360"),
                Button.inline("🎬 480p", b"adult_480"),
            ],
            [
                Button.inline("🎬 720p", b"adult_720"),
                Button.inline("🎬 1080p", b"adult_1080"),
            ],
            [Button.inline("❌ انصراف", b"adult_cancel")],
        ]
        await msg.edit(
            "🔞 لینک **بزرگسال** شناسایی شد!\n\nکیفیت مورد نظر را انتخاب کنید:",
            buttons=buttons,
        )
        if not hasattr(telegram_bot, "temp_data"):
            telegram_bot.temp_data = {}
        telegram_bot.temp_data[event.sender_id] = {
            "url": url,
            "step": "quality",
            "type": "adult",
            "status_msg": msg,
            "original_msg": event,
        }

    elif is_social_url(url):
        await msg.edit("🌐 لینک شبکه‌های اجتماعی...\n⏳ اضافه شد به صف")
        cancel_ev = asyncio.Event()
        _cancel_flags[event.sender_id] = cancel_ev
        pos = enqueue(
            {
                "type": "social",
                "url": url,
                "user_id": event.sender_id,
                "status_msg": msg,
                "original_msg": event,
                "cancel_event": cancel_ev,
            },
        )
        if pos > 1:
            await msg.edit(f"⏳ در صف انتظار — موقعیت: {pos}\n\nبرای لغو: /cancel")

    else:
        await msg.edit("🔗 لینک مستقیم...\n⏳ اضافه شد به صف")
        filename = (
            url.split(
                "/",
            )[-1].split("?")[0]
            or f"file_{event.message.id}.bin"
        )
        cancel_ev = asyncio.Event()
        _cancel_flags[event.sender_id] = cancel_ev
        pos = enqueue(
            {
                "type": "direct_url",
                "url": url,
                "filename": filename,
                "user_id": event.sender_id,
                "status_msg": msg,
                "original_msg": event,
                "cancel_event": cancel_ev,
            },
        )
        if pos > 1:
            await msg.edit(f"⏳ در صف انتظار — موقعیت: {pos}\n\nبرای لغو: /cancel")


# ==================== Callback Handler ====================
@telegram_bot.on(events.CallbackQuery)
async def callback_handler(event: events.CallbackQuery):
    user_id = event.sender_id
    data = event.data.decode()

    # handler های اختصاصی
    if (
        data.startswith("file_action:")
        or data.startswith("delete_confirm:")
        or data.startswith("delete_do:")
        or data.startswith("rename:")
        or data == "back_to_filelist"
    ):
        return

    if not hasattr(telegram_bot, "temp_data") or user_id not in telegram_bot.temp_data:
        await event.answer("❌ لطفاً دوباره لینک را بفرستید.", alert=True)
        return

    td = telegram_bot.temp_data[user_id]
    url = td["url"]
    status_msg = td.get("status_msg", event)
    original_msg = td.get("original_msg", event)

    if data.endswith("_cancel"):
        await event.edit("❌ عملیات لغو شد.")
        del telegram_bot.temp_data[user_id]
        return

    if data.startswith("adult_"):
        qmap = {
            "adult_360": "360",
            "adult_480": "480",
            "adult_720": "720",
            "adult_1080": "1080",
        }
        quality = qmap.get(data)
        if quality:
            del telegram_bot.temp_data[user_id]
            await event.edit(f"⏳ اضافه شد به صف — کیفیت {quality}p\n\nبرای لغو: /cancel")
            cancel_ev = asyncio.Event()
            _cancel_flags[user_id] = cancel_ev
            pos = enqueue(
                {
                    "type": "adult",
                    "url": url,
                    "quality": quality,
                    "user_id": user_id,
                    "status_msg": status_msg,
                    "original_msg": original_msg,
                    "cancel_event": cancel_ev,
                },
            )
            if pos > 1:
                await event.edit(f"⏳ در صف انتظار — موقعیت: {pos}\n\nبرای لغو: /cancel")

    elif data in ["yt_480", "yt_720", "yt_1080"]:
        qmap = {"yt_480": "480", "yt_720": "720", "yt_1080": "1080"}
        quality = qmap[data]
        del telegram_bot.temp_data[user_id]
        await event.edit(f"⏳ اضافه شد به صف — {quality}p\n\nبرای لغو: /cancel")
        cancel_ev = asyncio.Event()
        _cancel_flags[user_id] = cancel_ev
        pos = enqueue(
            {
                "type": "youtube",
                "url": url,
                "quality": quality,
                "user_id": user_id,
                "status_msg": status_msg,
                "original_msg": original_msg,
                "cancel_event": cancel_ev,
            },
        )
        if pos > 1:
            await event.edit(f"⏳ در صف انتظار — موقعیت: {pos}\n\nبرای لغو: /cancel")

    elif data == "yt_audio_first":
        telegram_bot.temp_data[user_id]["step"] = "bitrate"
        buttons = [
            [Button.inline("🔊 64 kbps", b"audio_64")],
            [Button.inline("🎵 128 kbps", b"audio_128")],
            [Button.inline("🎶 320 kbps", b"audio_320")],
            [Button.inline("↩️ بازگشت", b"back_to_quality")],
        ]
        await event.edit("🎵 Bitrate را انتخاب کنید:", buttons=buttons)

    elif data in ["audio_64", "audio_128", "audio_320"]:
        bitrate_map = {
            "audio_64": "64",
            "audio_128": "128",
            "audio_320": "320",
        }
        bitrate = bitrate_map[data]
        del telegram_bot.temp_data[user_id]
        await event.edit(f"⏳ اضافه شد به صف — صدا {bitrate}kbps\n\nبرای لغو: /cancel")
        cancel_ev = asyncio.Event()
        _cancel_flags[user_id] = cancel_ev
        pos = enqueue(
            {
                "type": "youtube",
                "url": url,
                "quality": "audio",
                "bitrate": bitrate,
                "user_id": user_id,
                "status_msg": status_msg,
                "original_msg": original_msg,
                "cancel_event": cancel_ev,
            },
        )
        if pos > 1:
            await event.edit(f"⏳ در صف انتظار — موقعیت: {pos}\n\nبرای لغو: /cancel")

    elif data == "back_to_quality":
        telegram_bot.temp_data[user_id]["step"] = "quality"
        buttons = [
            [
                Button.inline("🎬 480p", b"yt_480"),
                Button.inline("🎬 720p", b"yt_720"),
            ],
            [
                Button.inline("🎬 1080p", b"yt_1080"),
                Button.inline("🎵 فقط صوتی", b"yt_audio_first"),
            ],
            [Button.inline("❌ انصراف", b"yt_cancel")],
        ]
        await event.edit("🎬 کیفیت را انتخاب کنید:", buttons=buttons)


# ==================== main ====================
async def main() -> None:
    print("Telegram bot is starting...")
    print("Checking credentials...")
    _does_telegram_client_needs_reload: bool = False
    # If API ID is not set, get it from the user
    if load_api_id() == 1:
        # Get API ID
        print("API ID not found. Please enter it:")
        _api_id: int = int(input().strip())  # noqa: ASYNC250
        # Save API ID
        save_api_id(_api_id)
        # Set to reload the telegram client with new credentials
        _does_telegram_client_needs_reload = True

    # If API HASH is not set, get it from the user
    if load_api_hash() == "NOT_SET":
        # Get API HASH
        print("API HASH not found. Please enter it:")
        _api_hash: str = input().strip()  # noqa: ASYNC250
        # Save API HASH
        save_api_hash(_api_hash)
        # Set to reload the telegram client with the new credentials
        _does_telegram_client_needs_reload = True

    # If Bot Token is not set, get it from the user
    if not load_bot_token():
        # Get Bot Token
        print("Bot Token not found. Please enter it:")
        _bot_token: str = input().strip()  # noqa: ASYNC250
        # Save Bot Token
        save_bot_token(_bot_token)

    # Reload telegram client if required and start with new data
    if _does_telegram_client_needs_reload:
        updated_telegram_bot: TelegramClient = TelegramClient(
            SESSION_NAME,
            load_api_id(),
            load_api_hash(),
        )

        async with updated_telegram_bot:
            await updated_telegram_bot.start(bot_token=load_bot_token())
            print("Telegram client reloaded with new credentials.")
            await updated_telegram_bot.run_until_disconnected()
    else:
        # Else, use the existing client
        async with telegram_bot:  # pylint: disable=E0606
            await telegram_bot.start(bot_token=load_bot_token())
            print("Bot started successfully!")
            await telegram_bot.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
