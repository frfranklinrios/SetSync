from __future__ import annotations

from cifras_tool.config import settings


def build_ydl_opts(**overrides) -> dict:
    """Opções compartilhadas do yt-dlp (cookies, EJS, player clients)."""
    opts: dict = {
        "quiet": True,
        "no_warnings": True,
        # Deno (padrão) + Node como fallback no container
        "js_runtimes": {"deno": {}, "node": {}},
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "mweb", "android"],
            }
        },
        "http_headers": {
            "User-Agent": settings.youtube_user_agent
            or (
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
            )
        },
    }
    if settings.youtube_cookies_file:
        opts["cookiefile"] = settings.youtube_cookies_file
    elif settings.youtube_cookies_from_browser:
        browser = settings.youtube_cookies_from_browser.strip()
        if browser:
            opts["cookiesfrombrowser"] = (browser,)
    opts.update(overrides)
    return opts
