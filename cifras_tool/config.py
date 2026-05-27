from __future__ import annotations

import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


class Settings:
    max_audio_duration: int = int(os.getenv("CIFRAS_MAX_AUDIO_DURATION", "600"))
    tmp_dir: str = os.getenv("CIFRAS_TMP_DIR", str(_ROOT / "data" / "cifras_tmp"))
    output_dir: str = os.getenv(
        "CIFRAS_OUTPUT_DIR", str(_ROOT / "data" / "cifras_output")
    )
    youtube_user_agent: str | None = os.getenv("CIFRAS_YOUTUBE_USER_AGENT")
    youtube_cookies_file: str | None = os.getenv("CIFRAS_YOUTUBE_COOKIES_FILE")
    # Se true, o servidor nunca baixa áudio do YouTube (recomendado em VPS).
    youtube_no_server: bool = os.getenv("CIFRAS_YOUTUBE_NO_SERVER", "").lower() in (
        "1",
        "true",
        "yes",
    )


settings = Settings()

for _path in (settings.tmp_dir, settings.output_dir):
    Path(_path).mkdir(parents=True, exist_ok=True)
