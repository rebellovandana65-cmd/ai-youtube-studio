#!/usr/bin/env python3
"""Send a rendered preview to Telegram when repository secrets are configured."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()
    video = Path(sys.argv[1] if len(sys.argv) > 1 else "output/news-style-preview.mp4")
    if not token or not chat_id:
        print("Telegram preview skipped: add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID as GitHub Actions secrets.")
        return 0
    if not video.is_file():
        print(f"Telegram preview failed: video not found: {video}", file=sys.stderr)
        return 2

    boundary = "----NewsStudioTelegramBoundary"
    fields = {
        "chat_id": chat_id,
        "caption": "News Studio visual/audio preview (design test, not a real news bulletin).",
    }
    chunks: list[bytes] = []
    for key, value in fields.items():
        chunks.extend([
            f"--{boundary}\r\n".encode(),
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode(),
            value.encode(),
            b"\r\n",
        ])
    chunks.extend([
        f"--{boundary}\r\n".encode(),
        f'Content-Disposition: form-data; name="video"; filename="{video.name}"\r\n'.encode(),
        b"Content-Type: video/mp4\r\n\r\n",
        video.read_bytes(),
        b"\r\n",
        f"--{boundary}--\r\n".encode(),
    ])
    request = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendVideo",
        data=b"".join(chunks),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if not payload.get("ok"):
            print("Telegram API returned an unsuccessful response.", file=sys.stderr)
            return 1
        print("TELEGRAM_PREVIEW_SENT=true")
        return 0
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        print(f"Telegram delivery failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
