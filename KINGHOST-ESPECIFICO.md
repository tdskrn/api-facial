# 🏢 Configurações Específicas para KingHost VPS

## 🎯 Otimizações para Infraestrutura KingHost

### **Características da KingHost VPS**
- **Localização**: Data centers no Brasil
- **OS**: Ubuntu 20.04/22.04 LTS
- **Rede**: Conexão nacional otimizada
- **Backup**: Disponível via painel
- **Monitoramento**: Painel de controle integrado

---

## 🔧 Configurações Específicas

### **1. Otimização de Rede para Brasil**
```bash
# Configurar DNS brasileiros
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Otimizar TCP para conexões nacionais
echo 'net.core.rmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 16777216' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_rmem = 4096 65536 16777216' >> /etc/sysctl.conf
echo 'net.ipv4.tcp_wmem = 4096 65536 16777216' >> /etc/sysctl.conf
sysctl -p
```

### **2. Configuração de Timezone**
```bash
# Configurar fuso horário brasileiro
sudo timedatectl set-timezone America/Sao_Paulo

# Verificar
timedatectl status
date
```

### **3. Configuração de Locale**
```bash
# Configurar idioma português
sudo locale-gen pt_BR.UTF-8
sudo update-locale LANG=pt_BR.UTF-8

# Adicionar ao .bashrc
echo 'export LANG=pt_BR.UTF-8' >> ~/.bashrc
echo 'export LC_ALL=pt_BR.UTF-8' >> ~/.bashrc
```

---

## 🚀 Script de Deploy Otimizado para KingHost

```bash
#!/bin/bash
# Deploy otimizado para KingHost VPS

set -euo pipefail

# Configurações específicas KingHost
KINGHOST_OPTIMIZATIONS=true
BRAZIL_TIMEZONE=true
PT_BR_LOCALE=true

# Função para otimizações KingHost
optimize_for_kinghost() {
    echo "🇧🇷 Aplicando otimizações para KingHost..."
    
    # Timezone Brasil
    if [[ $BRAZIL_TIMEZONE == true ]]; then
        timedatectl set-timezone America/Sao_Paulo
    fi
    
    # Locale português
    if [[ $PT_BR_LOCALE == true ]]; then
        locale-gen pt_BR.UTF-8
        update-locale LANG=pt_BR.UTF-8
    fi
    
    # DNS brasileiros
    echo "nameserver 8.8.8.8" > /etc/resolv.conf
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf
    
    # Otimizações de rede
    cat >> /etc/sysctl.conf << EOF
# Otimizações KingHost
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 65536 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.ipv4.tcp_congestion_control = bbr
EOF
    sysctl -p
    
    echo "✅ Otimizações KingHost aplicadas"
}

# Configuração específica do Gunicorn para KingHost
setup_gunicorn_kinghost() {
    cat > /home/facial-api/api-facial/gunicorn-kinghost.conf.py << 'EOF'
#!/usr/bin/env python3
# Configuração Gunicorn otimizada para KingHost VPS

import multiprocessing
import os

# Configurações de servidor
bind = "127.0.0.1:8000"  # Apenas localhost para segurança
workers = 3  # Otimizado para VPS 4GB KingHost
worker_class = "sync"
worker_connections = 1000
max_requests = 800  # Menor para reciclar workers
max_requests_jitter = 100

# Timeouts otimizados para rede brasileira
timeout = 60  # Maior timeout para reconhecimento facial
keepalive = 3  # Manter conexões por mais tempo
graceful_timeout = 45

# Performance
preload_app = True
reload = False

# Logs
accesslog = '/home/facial-api/api-facial/logs/gunicorn_access.log'
errorlog = '/home/facial-api/api-facial/logs/gunicorn_error.log'
loglevel = 'info'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Segurança
proc_name = 'facial-api-kinghost'
daemon = False
pidfile = '/home/facial-api/api-facial/logs/gunicorn.pid'

# Otimizações específicas KingHost
if os.path.exists('/dev/shm'):
    worker_tmp_dir = '/dev/shm'  # Usar RAM para temp files

# Configurações por ambiente
if os.getenv('ENVIRONMENT') == 'production':
    workers = 3
    max_requests = 600
    timeout = 50
else:
    workers = 2
    reload = True
    loglevel = 'debug'

def on_starting(server):
    server.log.info("🚀 Iniciando Gunicorn para KingHost VPS")
    server.log.info(f"🌐 Workers: {workers}")
    server.log.info(f"⏱️  Timeout: {timeout}s")

def when_ready(server):
    server.log.info("✅ API de Reconhecimento Facial pronta na KingHost!")
    server.log.info("🇧🇷 Otimizada para infraestrutura brasileira")
EOF
}

# Configuração Nginx otimizada para KingHost
setup_nginx_kinghost() {
    cat > /etc/nginx/sites-available/facial-api << EOF
# Configuração Nginx otimizada para KingHost VPS
server {
    listen 80;
    server_name $DOMAIN;
    
    # Logs com formato brasileiro
    access_log /var/log/nginx/facial-api.access.log combined;
    error_log /var/log/nginx/facial-api.error.log warn;
    
    # Configurações para upload (otimizado para fotos brasileiras)
    client_max_body_size 20M;  # Fotos podem ser maiores
    client_body_timeout 45s;   # Timeout maior para upload
    client_header_timeout 30s;
    client_body_buffer_size 256k;
    
    # Compressão otimizada
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types
        application/json
        application/javascript
        text/plain
        text/css
        text/xml
        text/javascript
        image/svg+xml;
    
    # Headers de segurança
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    
    # Rate limiting para proteção
    limit_req_zone \$binary_remote_addr zone=api:10m rate=60r/m;
    limit_req zone=api burst=20 nodelay;
    
    # Proxy para aplicação
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Timeouts otimizados para reconhecimento facial
        proxy_connect_timeout 30s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer otimizado
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check sem logs
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Bloquear acesso a arquivos sensíveis
    location ~ /\.(ht|env) {
        deny all;
    }
    
    # Cache para arquivos estáticos
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|woff|woff2)\$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}
EOF
}

# Executar otimizações
if [[ \$KINGHOST_OPTIMIZATIONS == true ]]; then
    optimize_for_kinghost
    setup_gunicorn_kinghost
    setup_nginx_kinghost
fi
```

---

## 📊 Monitoramento Específico KingHost

### **Script de Monitoramento Brasileiro**
```bash
#!/bin/bash
# Monitor otimizado para KingHost

LOG_FILE="/var/log/facial-api-monitor-br.log"
DATE=$(date '+%d/%m/%Y %H:%M:%S')

# Função de log em português
log_br() {
    echo "[$DATE] $1" >> $LOG_FILE
}

# Verificar API
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    log_br "❌ API não está respondendo - reiniciando serviço"
    systemctl restart facial-api
    sleep 10
    
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log_br "✅ API reiniciada com sucesso"
    else
        log_br "🚨 ERRO CRÍTICO: API não conseguiu reiniciar"
        # Enviar alerta (implementar webhook se necessário)
    fi
fi

# Verificar uso de disco (em português)
DISK_USAGE=$(df /home/facial-api | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    log_br "⚠️ Uso de disco alto: ${DISK_USAGE}% - limpando logs"
    find /home/facial-api/api-facial/logs -name "*.log" -mtime +3 -delete
    find /var/log/nginx -name "*.log" -mtime +5 -delete
fi

# Verificar memória
MEM_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2 }')
if [ $MEM_USAGE -gt 90 ]; then
    log_br "⚠️ Uso de memória alto: ${MEM_USAGE}% - reiniciando aplicação"
    systemctl restart facial-api
fi

# Verificar conectividade com Laravel
if [[ -n "$LARAVEL_API_BASE" ]]; then
    if ! curl -f "$LARAVEL_API_BASE/api/health" > /dev/null 2>&1; then
        log_br "⚠️ Conectividade com Laravel falhou"
    fi
fi

log_br "✅ Monitoramento concluído - Sistema OK"
```

### **Configurar Cron para Monitoramento**
```bash
# Adicionar ao crontab
sudo crontab -e

# Monitoramento a cada 5 minutos
*/5 * * * * /home/facial-api/monitor-br.sh

# Backup diário às 2h da manhã
0 2 * * * /home/facial-api/backup-br.sh

# Limpeza semanal aos domingos às 3h
0 3 * * 0 /home/facial-api/cleanup-br.sh
```

---

## 🔒 Segurança Específica KingHost

### **Configuração de Firewall Brasileira**
```bash
#!/bin/bash
# Firewall otimizado para uso brasileiro

# Permitir IPs brasileiros (principais provedores)
ufw allow from 200.0.0.0/8
ufw allow from 201.0.0.0/8
ufw allow from 177.0.0.0/8

# Bloquear países com alto risco
# (implementar GeoIP se necessário)

# Rate limiting específico
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
```

### **Backup Automático para KingHost**
```bash
#!/bin/bash
# Backup otimizado para infraestrutura KingHost

BACKUP_DIR="/home/facial-api/backups"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

mkdir -p $BACKUP_DIR

# Backup compactado
tar -czf $BACKUP_DIR/facial-api-$DATE.tar.gz \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='venv' \
    /home/facial-api/api-facial

# Manter apenas últimos 7 dias
find $BACKUP_DIR -name "facial-api-*.tar.gz" -mtime +$RETENTION_DAYS -delete

# Log em português
echo "$(date '+%d/%m/%Y %H:%M:%S') - Backup criado: facial-api-$DATE.tar.gz" >> /var/log/backup-br.log

# Verificar se backup foi criado com sucesso
if [[ -f "$BACKUP_DIR/facial-api-$DATE.tar.gz" ]]; then
    echo "✅ Backup realizado com sucesso"
else
    echo "❌ Erro ao criar backup" >&2
    exit 1
fi
```

---

## 📞 Suporte KingHost

### **Informações para Suporte Técnico**
```bash
#!/bin/bash
# Coletar informações para suporte KingHost

INFO_FILE="kinghost-support-$(date +%Y%m%d_%H%M%S).txt"

echo "=== INFORMAÇÕES PARA SUPORTE KINGHOST ===" > $INFO_FILE
echo "Data: $(date '+%d/%m/%Y %H:%M:%S')" >> $INFO_FILE
echo "" >> $INFO_FILE

echo "=== SISTEMA ===" >> $INFO_FILE
uname -a >> $INFO_FILE
lsb_release -a >> $INFO_FILE
echo "" >> $INFO_FILE

echo "=== RECURSOS ===" >> $INFO_FILE
free -h >> $INFO_FILE
df -h >> $INFO_FILE
echo "" >> $INFO_FILE

echo "=== SERVIÇOS ===" >> $INFO_FILE
systemctl status facial-api nginx >> $INFO_FILE
echo "" >> $INFO_FILE

echo "=== REDE ===" >> $INFO_FILE
netstat -tlnp | grep -E "(80|443|8000)" >> $INFO_FILE
echo "" >> $INFO_FILE

echo "=== LOGS RECENTES ===" >> $INFO_FILE
journalctl -u facial-api -n 20 >> $INFO_FILE

echo "Arquivo criado: $INFO_FILE"
echo "Envie este arquivo para o suporte KingHost"
```

### **Contatos KingHost**
- **Suporte 24h**: 0800 721 8000
- **WhatsApp**: (51) 3550-3535
- **Chat**: Portal do cliente
- **Email**: suporte@kinghost.com.br
- **Emergência**: Através do painel de controle

---

## 🎯 Checklist Específico KingHost

### **Pré-Deploy**
- [ ] VPS KingHost contratada (mínimo 4GB RAM)
- [ ] Ubuntu 20.04+ instalado
- [ ] Acesso SSH configurado
- [ ] Domínio apontando para IP da VPS
- [ ] Firewall KingHost configurado no painel

### **Pós-Deploy**
- [ ] Timezone configurado para Brasil
- [ ] Locale português configurado
- [ ] DNS brasileiros configurados
- [ ] SSL Let's Encrypt instalado
- [ ] Monitoramento ativo
- [ ] Backup automático configurado
- [ ] Logs em português
- [ ] Rate limiting configurado

### **Otimizações**
- [ ] Gunicorn otimizado para KingHost
- [ ] Nginx com configurações brasileiras
- [ ] Compressão gzip ativa
- [ ] Cache configurado
- [ ] Segurança reforçada
- [ ] Monitoramento em tempo real

---

**🇧🇷 Sua API está otimizada para a infraestrutura KingHost!**

*Este guia foi desenvolvido especificamente para as características da KingHost VPS, garantindo máxima performance e compatibilidade.*