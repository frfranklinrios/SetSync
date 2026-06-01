"""Extensões Flask (scheduler de vouchers)."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

_scheduler: BackgroundScheduler | None = None


def init_scheduler(app) -> None:
    """Inicia job diário de vencimento de vouchers."""
    global _scheduler
    if _scheduler is not None:
        return
    if app.config.get('TESTING'):
        return

    _scheduler = BackgroundScheduler(daemon=True)

    def _job():
        with app.app_context():
            from scheduler_jobs import run_daily_voucher_jobs
            try:
                run_daily_voucher_jobs()
            except Exception as exc:
                app.logger.exception('Erro no job de vouchers: %s', exc)

    _scheduler.add_job(_job, 'cron', hour=6, minute=0, id='voucher_daily')
    _scheduler.start()
    app.logger.info('APScheduler: job diário de vouchers agendado (06:00 UTC)')
