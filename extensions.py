"""Extensões Flask (scheduler de vouchers)."""

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler

from config import app_timezone_name, app_tz

_scheduler: BackgroundScheduler | None = None


def init_scheduler(app) -> None:
    """Inicia job diário de vouchers."""
    global _scheduler
    if _scheduler is not None:
        return
    if app.config.get('TESTING'):
        return

    _tz = app_tz()
    _tz_name = app_timezone_name()

    _scheduler = BackgroundScheduler(daemon=True)

    def _job():
        with app.app_context():
            from scheduler_jobs import run_daily_voucher_jobs
            try:
                run_daily_voucher_jobs()
            except Exception as exc:
                app.logger.exception('Erro no job de vouchers: %s', exc)

    _scheduler.add_job(_job, 'cron', hour=6, minute=0, timezone=_tz, id='voucher_daily')
    _scheduler.start()
    app.logger.info('APScheduler: jobs diários (vouchers, onboarding, retenção) às 06:00 (%s)', _tz_name)

    def _agenda_job():
        with app.app_context():
            from scheduler_jobs import run_agenda_reminder_jobs
            try:
                run_agenda_reminder_jobs()
            except Exception as exc:
                app.logger.exception('Erro no job de lembretes da agenda: %s', exc)

    _scheduler.add_job(_agenda_job, 'cron', minute=0, timezone=_tz, id='agenda_reminders_hourly')
    app.logger.info('APScheduler: lembretes de agenda a cada hora (%s)', _tz_name)

    def _digest_job():
        with app.app_context():
            from scheduler_jobs import run_notification_digest_jobs
            try:
                run_notification_digest_jobs()
            except Exception as exc:
                app.logger.exception('Erro no resumo diário de notificações: %s', exc)

    _scheduler.add_job(
        _digest_job,
        'cron',
        hour=21,
        minute=0,
        timezone=_tz,
        id='notification_digest_daily',
    )
    app.logger.info(
        'APScheduler: resumo diário de notificações às 21:00 (%s)',
        _tz_name,
    )

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
