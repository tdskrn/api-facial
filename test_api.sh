#!/bin/bash
# Script de Teste para API de Reconhecimento Facial
# Versão: 1.0.0

set -e

# Configurações
API_URL="http://localhost:8000"
EMPLOYEE_ID="123"

# Cores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[TEST] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

# Função para testar endpoint
test_endpoint() {
    local method=$1
    local url=$2
    local description=$3
    
    log "Testando: $description"
    echo "  → $method $url"
    
    if curl -s -f -X $method "$url" > /dev/null; then
        echo -e "  ✅ ${GREEN}Sucesso${NC}"
    else
        echo -e "  ❌ ${RED}Falhou${NC}"
    fi
    echo ""
}

# Testes básicos da API
test_basic_endpoints() {
    echo "🧪 TESTANDO ENDPOINTS BÁSICOS"
    echo "==============================="
    
    test_endpoint "GET" "$API_URL/" "Endpoint raiz"
    test_endpoint "GET" "$API_URL/health" "Health check global"
    test_endpoint "GET" "$API_URL/api/v1/health" "Health check da API facial"
    test_endpoint "GET" "$API_URL/api/v1/statistics" "Estatísticas do sistema"
}

# Teste de funcionário (sem foto)
test_employee_endpoints() {
    echo "👤 TESTANDO GESTÃO DE FUNCIONÁRIOS"
    echo "==================================="
    
    test_endpoint "GET" "$API_URL/api/v1/employee/$EMPLOYEE_ID/status" "Status do funcionário $EMPLOYEE_ID"
}

# Teste com foto (se fornecida)
test_with_photo() {
    local photo_path=$1
    
    if [ ! -f "$photo_path" ]; then
        warn "Arquivo de foto não encontrado: $photo_path"
        warn "Para testar upload, forneça uma foto: ./test_api.sh foto.jpg"
        return
    fi
    
    echo "📷 TESTANDO COM FOTO"
    echo "===================="
    
    log "Registrando funcionário $EMPLOYEE_ID com foto..."
    if curl -s -f -X POST "$API_URL/api/v1/register-employee/$EMPLOYEE_ID" \
            -F "file=@$photo_path" > /dev/null; then
        echo -e "  ✅ ${GREEN}Funcionário registrado${NC}"
        
        log "Verificando funcionário..."
        if curl -s -f -X POST "$API_URL/api/v1/verify-face/$EMPLOYEE_ID" \
                -F "file=@$photo_path" > /dev/null; then
            echo -e "  ✅ ${GREEN}Verificação facial funcionou${NC}"
        else
            echo -e "  ❌ ${RED}Verificação facial falhou${NC}"
        fi
        
        log "Verificando status após registro..."
        curl -s "$API_URL/api/v1/employee/$EMPLOYEE_ID/status" | python3 -m json.tool
        
    else
        echo -e "  ❌ ${RED}Falha no registro${NC}"
    fi
}

# Teste de performance simples
test_performance() {
    echo "⚡ TESTE DE PERFORMANCE"
    echo "======================="
    
    log "Fazendo 10 requisições ao health check..."
    
    start_time=$(date +%s.%N)
    for i in {1..10}; do
        curl -s "$API_URL/health" > /dev/null
    done
    end_time=$(date +%s.%N)
    
    duration=$(echo "$end_time - $start_time" | bc)
    avg_time=$(echo "scale=3; $duration / 10" | bc)
    
    echo "  Tempo total: ${duration}s"
    echo "  Tempo médio por requisição: ${avg_time}s"
}

# Função principal
main() {
    echo "🎯 API de Reconhecimento Facial - Testes"
    echo "========================================="
    echo ""
    
    # Verificar se a API está rodando
    if ! curl -s "$API_URL/health" > /dev/null; then
        error "API não está respondendo em $API_URL"
        error "Certifique-se de que a API está rodando: ./deploy.sh status"
        exit 1
    fi
    
    log "API está respondendo! 🎉"
    echo ""
    
    # Executar testes
    test_basic_endpoints
    echo ""
    
    test_employee_endpoints
    echo ""
    
    # Se foi fornecida uma foto, testar upload
    if [ $# -gt 0 ]; then
        test_with_photo "$1"
        echo ""
    fi
    
    test_performance
    echo ""
    
    echo "✅ Testes concluídos!"
    echo ""
    echo "📚 Para ver a documentação completa: $API_URL/docs"
    echo "📊 Para ver estatísticas: $API_URL/api/v1/statistics"
}

# Executar
main "$@" 