import multiprocessing
import os

bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
chdir = os.getenv("GUNICORN_CHDIR", "/app/src")
workers = int(os.getenv("WEB_CONCURRENCY", min(4, (multiprocessing.cpu_count() * 2) + 1)))
threads = int(os.getenv("GUNICORN_THREADS", "2"))
worker_class = "gthread"
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = 30
keepalive = 5
max_requests = 1000
max_requests_jitter = 100
accesslog = "-"
errorlog = "-"
capture_output = True
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
