from __future__ import annotations

import uuid
from pathlib import Path

from yt_dlp import DownloadError, YoutubeDL
from yt_dlp.utils import ExtractorError

from cifras_tool.ydl_common import build_ydl_opts


class DownloaderError(Exception):
    pass


class VideoTooLongError(DownloaderError):
    pass


class VideoUnavailableError(DownloaderError):
    pass


class RegionBlockedError(DownloaderError):
    pass


class AudioDownloader:
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_as_wav_mono_22050(self, url: str) -> Path:
        file_id = uuid.uuid4().hex
        output_template = str(self.output_dir / f"{file_id}.%(ext)s")
        target_wav = self.output_dir / f"{file_id}.wav"

        ydl_opts = build_ydl_opts(
            format="bestaudio/best",
            outtmpl=output_template,
            noplaylist=True,
            socket_timeout=20,
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "wav",
                    "preferredquality": "0",
                }
            ],
            postprocessor_args=["-ac", "1", "-ar", "22050"],
        )

        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise VideoUnavailableError("Nao foi possivel obter metadados do video.")

                duration = int(info.get("duration") or 0)
                if duration > settings.max_audio_duration:
                    raise VideoTooLongError(
                        f"Video excede limite de {settings.max_audio_duration}s."
                    )

                ydl.download([url])
        except VideoTooLongError:
            raise
        except (ExtractorError, DownloadError) as err:
            message = str(err).lower()
            if "video unavailable" in message or "private video" in message:
                raise VideoUnavailableError("Video indisponivel ou privado.") from err
            if "not available in your country" in message or "geo" in message:
                raise RegionBlockedError("Video bloqueado por regiao.") from err
            if "sign in to confirm your age" in message:
                raise VideoUnavailableError("Video com restricao de idade.") from err
            raise DownloaderError(f"Falha ao baixar audio: {err}") from err
        except Exception as err:
            raise DownloaderError(f"Erro inesperado no downloader: {err}") from err

        if not target_wav.exists():
            raise DownloaderError("Arquivo WAV nao foi gerado pelo ffmpeg/yt-dlp.")

        return target_wav
