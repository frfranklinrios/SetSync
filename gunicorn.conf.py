import multiprocessing

# Workers: (2 * CPUs) + 1 is the standard recommendation
workers = multiprocessing.cpu_count() * 2 + 1

# Bind
bind = "0.0.0.0:5000"

# Timeouts — generous to survive slow Google OAuth / email calls
timeout = 120
graceful_timeout = 30
keepalive = 5

# Logging — send to stdout/stderr so docker logs picks them up
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s "%(r)s" %(s)s %(b)s %(D)sµs'

# Restart workers after N requests to prevent memory leaks
max_requests = 1000
max_requests_jitter = 100
