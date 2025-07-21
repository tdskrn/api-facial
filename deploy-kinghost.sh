#!/bin/bash
# 🚀 Script de Deploy para VPS KingHost
# API de Reconhecimento Facial - Flask Version
# Versão: 1.0.0

set -euo pipefail

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configurações
PROJECT_NAME="facial-api"
PROJECT_DIR="/var/www/facial-api"
NGINX_SITE="/etc/nginx/sites-available/facial-api"
SERVICE_NAME="facial-api"
PYTHON_VERSION="3.10"

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

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "Este script não deve ser executado como root. Use seu usuário normal."
    fi
}

# Instalar dependências do sistema Ubuntu
install_system_deps() {
    log "📦 Instalando dependências do sistema..."
    
    sudo apt update
    sudo apt install -y \
        python3-pip \
        python3-dev \
        python3-venv \
        build-essential \
        libssl-dev \
        libffi-dev \
        python3-setuptools \
        libjpeg-dev \
        libpng-dev \
        libopencv-dev \
        cmake \
        libatlas-base-dev \
        liblapack-dev \
        libx11-dev \
        libgtk-3-dev \
        nginx \
        supervisor
    
    log "✅ Dependências do sistema instaladas"
}

# Criar estrutura de diretórios
setup_directories() {
    log "📁 Criando estrutura de diretórios..."
    
    sudo mkdir -p $PROJECT_DIR
    sudo chown $USER:$USER $PROJECT_DIR
    mkdir -p $PROJECT_DIR/logs
    
    log "✅ Diretórios criados"
}

# Copiar arquivos do projeto
copy_project_files() {
    log "📋 Copiando arquivos do projeto..."
    
    # Copiar arquivos principais
    cp app.py $PROJECT_DIR/
    cp gunicorn.conf.py $PROJECT_DIR/
    cp requirements-flask.txt $PROJECT_DIR/requirements.txt
    cp -r utils $PROJECT_DIR/
    
    # Criar arquivo .env
    if [ ! -f $PROJECT_DIR/.env ]; then
        log "📝 Criando arquivo .env..."
        cat > $PROJECT_DIR/.env << EOF
# Configurações da API de Reconhecimento Facial
DEBUG=false
SECRET_KEY=$(openssl rand -hex 32)
PORT=8000
ENVIRONMENT=production

# Integração com Laravel (OBRIGATÓRIO - CONFIGURE ANTES DE USAR)
LARAVEL_API_BASE=https://meusite-laravel.com.br
LARAVEL_API_TOKEN=

# Reconhecimento facial
FACE_TOLERANCE=0.6
MAX_FILE_SIZE=10485760

# Logs
LOG_LEVEL=INFO
EOF
        log "✅ Arquivo .env criado"
    else
        log "ℹ️  Arquivo .env já existe"
    fi
    
    log "✅ Arquivos copiados"
}

# Criar ambiente virtual Python
setup_python_env() {
    log "🐍 Configurando ambiente Python..."
    
    cd $PROJECT_DIR
    
    # Criar ambiente virtual
    python3 -m venv venv
    source venv/bin/activate
    
    # Atualizar pip
    pip install --upgrade pip setuptools wheel
    
    # Instalar dependências
    log "📦 Instalando dependências Python..."
    pip install -r requirements.txt
    
    log "✅ Ambiente Python configurado"
}

# Testar a aplicação
test_application() {
    log "🧪 Testando aplicação..."
    
    cd $PROJECT_DIR
    source venv/bin/activate
    
    # Teste básico de importação
    python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from app import app
    print('✅ Aplicação Flask carregada com sucesso')
except ImportError as e:
    print(f'❌ Erro de importação: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Erro na aplicação: {e}')
    sys.exit(1)
"
    
    # Teste das dependências de reconhecimento facial
    python3 -c "
try:
    import face_recognition
    import cv2
    import numpy as np
    from PIL import Image
    print('✅ Bibliotecas de reconhecimento facial OK')
except ImportError as e:
    print(f'⚠️ Dependência faltando: {e}')
    print('A API funcionará em modo limitado')
"
    
    log "✅ Testes básicos concluídos"
}

# Configurar Nginx
setup_nginx() {
    log "🌐 Configurando Nginx..."
    
    # Copiar configuração do Nginx
    sudo cp nginx-flask.conf $NGINX_SITE
    
    # Editar configuração básica (usuário deve ajustar o domínio)
    warn "⚠️  Lembre-se de editar o domínio em: $NGINX_SITE"
    
    # Habilitar site
    sudo ln -sf $NGINX_SITE /etc/nginx/sites-enabled/
    
    # Remover site padrão se existir
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Testar configuração
    sudo nginx -t
    
    # Recarregar Nginx
    sudo systemctl reload nginx
    sudo systemctl enable nginx
    
    log "✅ Nginx configurado"
}

# Criar serviço systemd
create_systemd_service() {
    log "🛠️  Criando serviço systemd..."
    
    sudo tee /etc/systemd/system/$SERVICE_NAME.service > /dev/null << EOF
[Unit]
Description=API de Reconhecimento Facial
After=network.target

[Service]
Type=notify
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Recarregar systemd
    sudo systemctl daemon-reload
    sudo systemctl enable $SERVICE_NAME
    
    log "✅ Serviço systemd criado"
}

# Configurar firewall (UFW)
setup_firewall() {
    log "🔥 Configurando firewall..."
    
    # Instalar UFW se não estiver instalado
    sudo apt install -y ufw
    
    # Configurações básicas
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    
    # Permitir SSH (importante!)
    sudo ufw allow ssh
    sudo ufw allow 22
    
    # Permitir HTTP e HTTPS
    sudo ufw allow 80
    sudo ufw allow 443
    
    # Habilitar firewall
    sudo ufw --force enable
    
    log "✅ Firewall configurado"
}

# Configurar logrotate
setup_logrotate() {
    log "📊 Configurando rotação de logs..."
    
    sudo tee /etc/logrotate.d/facial-api > /dev/null << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 $USER $USER
}
EOF
    
    log "✅ Logrotate configurado"
}

# Iniciar serviços
start_services() {
    log "🚀 Iniciando serviços..."
    
    # Iniciar aplicação
    sudo systemctl start $SERVICE_NAME
    sudo systemctl status $SERVICE_NAME --no-pager -l
    
    # Aguardar inicialização
    sleep 5
    
    # Testar se a API está respondendo
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log "✅ API está respondendo!"
    else
        error "❌ API não está respondendo. Verifique os logs: sudo journalctl -u $SERVICE_NAME -f"
    fi
    
    log "✅ Serviços iniciados"
}

# Mostrar informações finais
show_info() {
    echo ""
    log "🎉 Deploy concluído com sucesso!"
    echo ""
    echo -e "${BLUE}📋 Informações importantes:${NC}"
    echo "   🌐 API: http://$(hostname -I | awk '{print $1}'):8000"
    echo "   📚 Health Check: http://$(hostname -I | awk '{print $1}'):8000/health"
    echo "   📁 Projeto: $PROJECT_DIR"
    echo "   📊 Logs: $PROJECT_DIR/logs/"
    echo ""
    echo -e "${BLUE}🔧 Comandos úteis:${NC}"
    echo "   📋 Status: sudo systemctl status $SERVICE_NAME"
    echo "   🔄 Reiniciar: sudo systemctl restart $SERVICE_NAME"
    echo "   📊 Logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "   🛑 Parar: sudo systemctl stop $SERVICE_NAME"
    echo ""
    echo -e "${YELLOW}⚠️  Próximos passos:${NC}"
    echo "   1. Edite o domínio em: $NGINX_SITE"
    echo "   2. Configure SSL com Let's Encrypt"
    echo "   3. Ajuste a BASE_URL no arquivo .env"
    echo "   4. Monitore os logs regularmente"
    echo ""
}

# Função para backup
backup_current() {
    if [ -d "$PROJECT_DIR" ]; then
        log "💾 Fazendo backup da instalação atual..."
        BACKUP_NAME="facial-api-backup-$(date +%Y%m%d_%H%M%S).tar.gz"
        sudo tar -czf "/tmp/$BACKUP_NAME" -C "$(dirname $PROJECT_DIR)" "$(basename $PROJECT_DIR)"
        log "✅ Backup salvo: /tmp/$BACKUP_NAME"
    fi
}

# Menu principal
main() {
    echo -e "${BLUE}"
    echo "🧠 Deploy API de Reconhecimento Facial - VPS KingHost"
    echo "====================================================="
    echo -e "${NC}"
    
    case "${1:-}" in
        "install")
            check_root
            install_system_deps
            setup_directories
            copy_project_files
            setup_python_env
            test_application
            setup_nginx
            create_systemd_service
            setup_firewall
            setup_logrotate
            start_services
            show_info
            ;;
        "update")
            check_root
            backup_current
            copy_project_files
            cd $PROJECT_DIR && source venv/bin/activate && pip install -r requirements.txt
            test_application
            sudo systemctl restart $SERVICE_NAME
            log "✅ Atualização concluída"
            ;;
        "status")
            sudo systemctl status $SERVICE_NAME
            curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "API não está respondendo"
            ;;
        "logs")
            sudo journalctl -u $SERVICE_NAME -f
            ;;
        "restart")
            sudo systemctl restart $SERVICE_NAME
            log "✅ Serviço reiniciado"
            ;;
        "stop")
            sudo systemctl stop $SERVICE_NAME
            log "✅ Serviço parado"
            ;;
        "start")
            sudo systemctl start $SERVICE_NAME
            log "✅ Serviço iniciado"
            ;;
        *)
            echo "Uso: $0 {install|update|status|logs|restart|stop|start}"
            echo ""
            echo "Comandos disponíveis:"
            echo "  install  - Instalação completa (primeira vez)"
            echo "  update   - Atualizar código e dependências"
            echo "  status   - Verificar status do serviço"
            echo "  logs     - Visualizar logs em tempo real"
            echo "  restart  - Reiniciar serviço"
            echo "  stop     - Parar serviço"
            echo "  start    - Iniciar serviço"
            echo ""
            echo "Exemplos:"
            echo "  $0 install   # Primeira instalação"
            echo "  $0 update    # Atualizar código"
            echo "  $0 status    # Ver status"
            echo ""
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"