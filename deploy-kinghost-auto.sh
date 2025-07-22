#!/bin/bash
# 🚀 Script Automatizado de Deploy para KingHost VPS
# API de Reconhecimento Facial - Versão Simplificada
# Execute como: bash deploy-kinghost-auto.sh

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PROJECT_NAME="facial-api"
PROJECT_USER="facial-api"
PROJECT_DIR="/home/facial-api/api-facial"
DOMAIN=""
LARAVEL_API_BASE=""
LARAVEL_API_TOKEN=""

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️  $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] ℹ️  $1${NC}"
}

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "🧠 API de Reconhecimento Facial - Deploy KingHost VPS"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "Este script deve ser executado como root. Use: sudo bash $0"
    fi
}

# Coletar informações do usuário
collect_info() {
    log "📋 Coletando informações para o deploy..."
    
    echo -n "🌐 Digite seu domínio (ex: api-facial.seusite.com.br): "
    read -r DOMAIN
    
    echo -n "🔗 Digite a URL base do seu Laravel (ex: https://meusite.com.br): "
    read -r LARAVEL_API_BASE
    
    echo -n "🔑 Digite o token Bearer do Laravel: "
    read -r LARAVEL_API_TOKEN
    
    if [[ -z "$DOMAIN" || -z "$LARAVEL_API_BASE" || -z "$LARAVEL_API_TOKEN" ]]; then
        error "Todas as informações são obrigatórias!"
    fi
    
    info "Domínio: $DOMAIN"
    info "Laravel API: $LARAVEL_API_BASE"
    info "Token configurado: ${LARAVEL_API_TOKEN:0:10}..."
    
    echo -n "✅ Confirma as informações? (y/N): "
    read -r confirm
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        error "Deploy cancelado pelo usuário."
    fi
}

# Atualizar sistema
update_system() {
    log "🔄 Atualizando sistema..."
    apt update && apt upgrade -y
    apt install -y curl wget git nano htop unzip ufw
}

# Configurar firewall
setup_firewall() {
    log "🔥 Configurando firewall..."
    ufw allow OpenSSH
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
}

# Criar usuário da aplicação
create_user() {
    log "👤 Criando usuário da aplicação..."
    
    if id "$PROJECT_USER" &>/dev/null; then
        warn "Usuário $PROJECT_USER já existe."
    else
        adduser --disabled-password --gecos "" $PROJECT_USER
        usermod -aG sudo $PROJECT_USER
    fi
    
    # Configurar SSH
    mkdir -p /home/$PROJECT_USER/.ssh
    if [[ -f ~/.ssh/authorized_keys ]]; then
        cp ~/.ssh/authorized_keys /home/$PROJECT_USER/.ssh/
        chown -R $PROJECT_USER:$PROJECT_USER /home/$PROJECT_USER/.ssh
        chmod 700 /home/$PROJECT_USER/.ssh
        chmod 600 /home/$PROJECT_USER/.ssh/authorized_keys
    fi
}

# Instalar Python e dependências
install_python() {
    log "🐍 Instalando Python e dependências..."
    
    apt install -y python3 python3-pip python3-venv python3-dev
    apt install -y build-essential cmake libopenblas-dev liblapack-dev
    apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
    apt install -y libgomp1 libx11-dev libgtk-3-dev
    
    python3 --version
}

# Clonar e configurar aplicação
setup_application() {
    log "📁 Configurando aplicação..."
    
    # Mudar para usuário da aplicação
    sudo -u $PROJECT_USER bash << EOF
cd /home/$PROJECT_USER

# Clonar repositório se não existir
if [[ ! -d "api-facial" ]]; then
    git clone https://github.com/SEU_USUARIO/api-facial.git
fi

cd api-facial

# Criar ambiente virtual
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
fi

source venv/bin/activate

# Atualizar pip e instalar dependências
pip install --upgrade pip
pip install -r requirements.txt

# Tentar instalar dependências de reconhecimento facial
echo "📸 Instalando dependências de reconhecimento facial..."
pip install face-recognition opencv-python-headless numpy Pillow || {
    echo "⚠️  Aviso: Algumas dependências de reconhecimento facial falharam."
    echo "A API funcionará em modo limitado."
}

# Criar diretórios
mkdir -p logs
mkdir -p app/storage/employee_photos
mkdir -p app/storage/temp
chmod 755 logs app/storage
EOF
}

# Configurar variáveis de ambiente
setup_env() {
    log "⚙️  Configurando variáveis de ambiente..."
    
    cat > $PROJECT_DIR/.env << EOF
# Configurações básicas
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
PORT=8000
ENVIRONMENT=production

# Integração com Laravel
LARAVEL_API_BASE=$LARAVEL_API_BASE
LARAVEL_API_TOKEN=$LARAVEL_API_TOKEN

# Reconhecimento facial
FACE_TOLERANCE=0.6
MAX_FILE_SIZE=10485760

# Logs
LOG_LEVEL=INFO
EOF
    
    chown $PROJECT_USER:$PROJECT_USER $PROJECT_DIR/.env
    chmod 600 $PROJECT_DIR/.env
}

# Configurar systemd service
setup_service() {
    log "🔄 Configurando serviço systemd..."
    
    cat > /etc/systemd/system/facial-api.service << EOF
[Unit]
Description=🧠 API de Reconhecimento Facial para Ponto Eletrônico
After=network.target
Wants=network.target

[Service]
Type=notify
User=$PROJECT_USER
Group=$PROJECT_USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
    
    systemctl daemon-reload
    systemctl enable facial-api
}

# Instalar e configurar Nginx
setup_nginx() {
    log "🌐 Configurando Nginx..."
    
    apt install -y nginx
    
    cat > /etc/nginx/sites-available/facial-api << EOF
server {
    listen 80;
    server_name $DOMAIN;
    
    # Logs
    access_log /var/log/nginx/facial-api.access.log;
    error_log /var/log/nginx/facial-api.error.log;
    
    # Configurações para upload
    client_max_body_size 15M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    
    # Proxy para aplicação
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/facial-api /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t
    systemctl restart nginx
}

# Configurar SSL
setup_ssl() {
    log "🔒 Configurando SSL..."
    
    apt install -y certbot python3-certbot-nginx
    
    echo "📋 Para configurar SSL, execute manualmente:"
    echo "certbot --nginx -d $DOMAIN"
    
    # Configurar renovação automática
    (crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -
}

# Iniciar serviços
start_services() {
    log "🚀 Iniciando serviços..."
    
    systemctl start facial-api
    systemctl status facial-api --no-pager
    
    sleep 5
    
    # Testar aplicação
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        log "✅ Aplicação está rodando corretamente!"
    else
        error "❌ Aplicação não está respondendo. Verifique os logs: journalctl -u facial-api -f"
    fi
}

# Mostrar informações finais
show_final_info() {
    log "🎉 Deploy concluído com sucesso!"
    
    echo -e "${GREEN}"
    echo "═══════════════════════════════════════════════════════════════"
    echo "✅ DEPLOY CONCLUÍDO"
    echo "═══════════════════════════════════════════════════════════════"
    echo "🌐 URL da API: http://$DOMAIN"
    echo "🔍 Health Check: http://$DOMAIN/health"
    echo "📊 Status do serviço: systemctl status facial-api"
    echo "📋 Logs: journalctl -u facial-api -f"
    echo ""
    echo "🔒 Para configurar SSL:"
    echo "   certbot --nginx -d $DOMAIN"
    echo ""
    echo "🧪 Teste a API:"
    echo "   curl http://$DOMAIN/health"
    echo "═══════════════════════════════════════════════════════════════"
    echo -e "${NC}"
}

# Função principal
main() {
    show_banner
    check_root
    collect_info
    
    log "🚀 Iniciando deploy automatizado..."
    
    update_system
    setup_firewall
    create_user
    install_python
    setup_application
    setup_env
    setup_service
    setup_nginx
    setup_ssl
    start_services
    
    show_final_info
}

# Executar apenas se chamado diretamente
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi