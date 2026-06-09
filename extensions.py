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
    app.logger.info('APScheduler: jobs diários (vouchers, onboarding, retenção) às 06:00 UTC')

    def _agenda_job():
        with app.app_context():
            from scheduler_jobs import run_agenda_reminder_jobs
            try:
                run_agenda_reminder_jobs()
            except Exception as exc:
                app.logger.exception('Erro no job de lembretes da agenda: %s', exc)

    _scheduler.add_job(_agenda_job, 'cron', minute=0, id='agenda_reminders_hourly')
    app.logger.info('APScheduler: lembretes de agenda a cada hora (24h antes do evento)')

    _init_whatsapp_server(app)


def _init_whatsapp_server(app) -> None:
    """Garante instância Evolution ao subir (provider evolution)."""
    from whatsapp_config import whatsapp_provider

    if whatsapp_provider() != 'evolution':
        return
    with app.app_context():
        try:
            from whatsapp_server.client import ensure_instance, is_reachable

            if not is_reachable():
                app.logger.warning(
                    'Evolution API indisponível — WhatsApp ficará offline até o container subir'
                )
                return
            if ensure_instance():
                app.logger.info('WhatsApp Evolution: instância pronta')
        except Exception as exc:
            app.logger.warning('WhatsApp Evolution: init falhou: %s', exc)
