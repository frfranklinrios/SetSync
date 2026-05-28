import multiprocessing
import os

# SQLite: um único processo evita "database is locked" (Contabo / Docker).
# Concorrência via threads (worker_class gthread).
workers = int(os.getenv('GUNICORN_WORKERS', '1'))
threads = int(os.getenv('GUNICORN_THREADS', '4'))
worker_class = 'gthread' if threads > 1 else 'sync'

bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')

timeout = int(os.getenv('GUNICORN_TIMEOUT', '120'))
graceful_timeout = 30
keepalive = 5

accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sµs'

max_requests = 1000
max_requests_jitter = 100
