"""Ponto de entrada do SetSync: `uv run app.py` ou `uv run python main.py`."""
from __future__ import annotations

import os


def main() -> None:
    from app import app

    host = os.getenv("FLASK_RUN_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_RUN_PORT", "5000"))
    debug = os.getenv("FLASK_ENV", "development") == "development"
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
