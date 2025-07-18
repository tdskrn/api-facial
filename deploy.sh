#!/bin/bash
# Script de Deploy para API de Reconhecimento Facial na Hetzner Cloud
# Versão: 1.0.0
# Autor: API Facial Team

set -euo pipefail  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Verificar se o Docker está instalado
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker não está instalado. Por favor, instale o Docker primeiro."
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    fi
    
    log "✅ Docker e Docker Compose encontrados"
}

# Criar arquivo .env se não existir
setup_environment() {
    if [ ! -f .env ]; then
        log "📝 Criando arquivo .env..."
        
        # Gerar chave secreta aleatória
        SECRET_KEY=$(openssl rand -hex 32)
        
        cat > .env << EOF
# Configurações da API de Reconhecimento Facial
DEBUG=false
SECRET_KEY=${SECRET_KEY}

# Configurações de banco de dados
POSTGRES_DB=facial_api
POSTGRES_USER=facial_user
POSTGRES_PASSWORD=$(openssl rand -hex 16)

# Redis
REDIS_PASSWORD=$(openssl rand -hex 16)

# Grafana
GRAFANA_PASSWORD=$(openssl rand -hex 12)

# Para produção, configure seu domínio
DOMAIN=localhost
EOF
        
        log "✅ Arquivo .env criado com senhas seguras"
        warn "⚠️  IMPORTANTE: Backup do arquivo .env criado. Guarde as senhas em local seguro!"
    else
        log "✅ Arquivo .env já existe"
    fi
}

# Fazer backup das fotos existentes
backup_data() {
    if [ -d "app/storage/employee_photos" ] && [ "$(ls -A app/storage/employee_photos)" ]; then
        BACKUP_NAME="backup_photos_$(date +%Y%m%d_%H%M%S).tar.gz"
        log "💾 Fazendo backup das fotos existentes..."
        
        tar -czf "${BACKUP_NAME}" app/storage/employee_photos/
        
        log "✅ Backup salvo como: ${BACKUP_NAME}"
        log "📂 Localização: $(pwd)/${BACKUP_NAME}"
    else
        log "ℹ️  Nenhuma foto encontrada para backup"
    fi
}

# Parar containers existentes
stop_containers() {
    log "📦 Parando containers existentes..."
    
    if docker-compose ps -q 2>/dev/null | grep -q .; then
        docker-compose down
        log "✅ Containers parados"
    else
        log "ℹ️  Nenhum container estava rodando"
    fi
}

# Construir e iniciar aplicação
deploy_application() {
    log "🏗️  Construindo e iniciando aplicação..."
    
    # Para desenvolvimento (apenas API)
    if [ "${1:-production}" = "development" ]; then
        log "🔧 Modo desenvolvimento - apenas API"
        docker-compose up --build -d facial-api
    else
        # Para produção (com Nginx)
        log "🚀 Modo produção - com Nginx"
        docker-compose up --build -d facial-api nginx
    fi
    
    log "✅ Aplicação iniciada"
}

# Verificar saúde da aplicação
health_check() {
    log "🔍 Verificando saúde da aplicação..."
    
    # Aguardar a aplicação inicializar
    sleep 15
    
    # Verificar API
    if curl -f -s http://localhost:8000/health > /dev/null; then
        log "✅ API respondendo corretamente"
    else
        error "❌ API não está respondendo. Verifique os logs: docker-compose logs facial-api"
    fi
    
    # Verificar Nginx (se estiver rodando)
    if docker-compose ps nginx 2>/dev/null | grep -q Up; then
        if curl -f -s http://localhost/health > /dev/null; then
            log "✅ Nginx respondendo corretamente"
        else
            warn "⚠️  Nginx pode ter problemas. Verifique: docker-compose logs nginx"
        fi
    fi
}

# Mostrar status dos containers
show_status() {
    log "📊 Status dos containers:"
    docker-compose ps
    
    echo ""
    log "📋 Informações importantes:"
    echo "   🌐 API: http://localhost:8000"
    echo "   📚 Documentação: http://localhost:8000/docs"
    echo "   🔍 Health Check: http://localhost:8000/health"
    
    if docker-compose ps nginx 2>/dev/null | grep -q Up; then
        echo "   🌍 Nginx: http://localhost"
    fi
    
    echo ""
    log "🔧 Comandos úteis:"
    echo "   📋 Ver logs: docker-compose logs -f"
    echo "   🔄 Reiniciar: docker-compose restart"
    echo "   🛑 Parar: docker-compose down"
    echo "   📊 Status: docker-compose ps"
}

# Instalar Docker (Ubuntu/Debian)
install_docker() {
    log "🐳 Instalando Docker..."
    
    # Atualizar pacotes
    sudo apt-get update
    
    # Instalar dependências
    sudo apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # Adicionar chave GPG do Docker
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Adicionar repositório do Docker
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Instalar Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Instalar Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER
    
    log "✅ Docker instalado com sucesso!"
    warn "⚠️  IMPORTANTE: Faça logout e login novamente para usar Docker sem sudo"
}

# Menu principal
main() {
    echo -e "${BLUE}"
    echo "🎯 API de Reconhecimento Facial - Deploy Script"
    echo "============================================="
    echo -e "${NC}"
    
    case "${1:-}" in
        "install-docker")
            install_docker
            ;;
        "development")
            check_docker
            setup_environment
            backup_data
            stop_containers
            deploy_application "development"
            health_check
            show_status
            ;;
        "production")
            check_docker
            setup_environment
            backup_data
            stop_containers
            deploy_application "production"
            health_check
            show_status
            ;;
        "stop")
            stop_containers
            log "✅ Aplicação parada"
            ;;
        "logs")
            docker-compose logs -f
            ;;
        "status")
            show_status
            ;;
        "backup")
            backup_data
            ;;
        *)
            echo "Uso: $0 {install-docker|development|production|stop|logs|status|backup}"
            echo ""
            echo "Comandos disponíveis:"
            echo "  install-docker  - Instala Docker e Docker Compose (Ubuntu/Debian)"
            echo "  development     - Deploy em modo desenvolvimento (apenas API)"
            echo "  production      - Deploy em modo produção (API + Nginx)"
            echo "  stop           - Para todos os containers"
            echo "  logs           - Mostra logs em tempo real"
            echo "  status         - Mostra status dos containers"
            echo "  backup         - Faz backup das fotos"
            echo ""
            echo "Exemplos:"
            echo "  $0 install-docker    # Primeira vez no servidor"
            echo "  $0 production        # Deploy completo"
            echo "  $0 development       # Deploy para desenvolvimento"
            echo ""
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@" 