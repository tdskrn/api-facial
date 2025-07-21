#!/usr/bin/env python3
"""
🚀 Configuração do Gunicorn para API de Reconhecimento Facial
Otimizado para VPS KingHost com 4GB RAM
"""

import multiprocessing
import os

# Configurações do servidor
bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada
worker_class = "sync"  # Para aplicações com CPU intensiva (reconhecimento facial)
worker_connections = 1000
max_requests = 1000  # Reinicia worker após N requests (previne memory leaks)
max_requests_jitter = 50  # Adiciona variação aleatória ao max_requests

# Timeouts
timeout = 60  # Timeout para requests (reconhecimento facial pode demorar)
keepalive = 2
graceful_timeout = 30

# Processos
preload_app = True  # Carrega app antes de fazer fork (economia de memória)
reload = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

# Logs
accesslog = 'logs/gunicorn_access.log'
errorlog = 'logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Process naming
proc_name = 'facial-api'

# Server mechanics
daemon = False  # Para uso com systemd
pidfile = 'logs/gunicorn.pid'
user = None  # Deixe None para usar o usuário atual
group = None
tmp_upload_dir = None

# Worker tuning específico para reconhecimento facial
worker_tmp_dir = '/dev/shm'  # Usar RAM para arquivos temporários (se disponível)

# Configurações específicas para VPS KingHost
# Otimizado para 4GB RAM e cargas de pico
if os.getenv('ENVIRONMENT') == 'production':
    workers = 4  # 4 workers para 4GB RAM
    worker_class = "sync"
    max_requests = 500  # Menor para reciclar workers mais frequentemente
    timeout = 45  # Timeout menor em produção
else:
    # Configurações de desenvolvimento
    workers = 2
    reload = True
    loglevel = 'debug'

# Funções de callback para monitoramento
def on_starting(server):
    """Executado quando o master process inicia"""
    server.log.info("🚀 Iniciando API de Reconhecimento Facial")
    server.log.info(f"👥 Workers: {workers}")
    server.log.info(f"🌐 Bind: {bind}")

def on_reload(server):
    """Executado quando a aplicação é recarregada"""
    server.log.info("🔄 Recarregando aplicação...")

def worker_int(worker):
    """Executado quando worker recebe SIGINT"""
    worker.log.info(f"💤 Worker {worker.pid} recebeu sinal de interrupção")

def pre_fork(server, worker):
    """Executado antes do fork de cada worker"""
    server.log.info(f"🍴 Iniciando worker {worker.age}")

def post_fork(server, worker):
    """Executado após fork de cada worker"""
    server.log.info(f"✅ Worker {worker.pid} iniciado (worker {worker.age})")

def pre_exec(server):
    """Executado antes de exec() durante reload"""
    server.log.info("🔄 Preparando reload...")

def when_ready(server):
    """Executado quando servidor está pronto para aceitar conexões"""
    server.log.info("🎯 API pronta para receber requisições!")
    server.log.info("📚 Documentação: consulte README.md")

def worker_abort(worker):
    """Executado quando worker é abortado"""
    worker.log.error(f"💥 Worker {worker.pid} foi abortado!")

def pre_request(worker, req):
    """Executado antes de cada request"""
    worker.log.debug(f"📨 {req.method} {req.path}")

def post_request(worker, req, environ, resp):
    """Executado após cada request"""
    worker.log.debug(f"📤 {req.method} {req.path} - {resp.status}")

# Configurações SSL (para HTTPS com certificado)
# Descomente e configure se usar SSL
# keyfile = '/path/to/ssl/private.key'
# certfile = '/path/to/ssl/certificate.crt'
# ssl_version = 2  # TLS 1.2
# cert_reqs = 0    # ssl.CERT_NONE
# ca_certs = None
# suppress_ragged_eofs = True
# do_handshake_on_connect = False
# ciphers = 'TLSv1'