# 🔍 Como Testar Rotas Disponíveis no Servidor

## 🎯 Para API de Reconhecimento Facial (FastAPI)

### **1. Documentação Automática (Swagger)**
```bash
# Acessar documentação interativa
curl http://arcanun-tech.vps-kinghost.net/docs

# Ou no navegador:
# http://arcanun-tech.vps-kinghost.net/docs
```

### **2. OpenAPI Schema (JSON)**
```bash
# Obter schema completo da API
curl http://arcanun-tech.vps-kinghost.net/openapi.json | jq .

# Salvar schema em arquivo
curl http://arcanun-tech.vps-kinghost.net/openapi.json > api-schema.json
```

### **3. Endpoint Raiz (Informações da API)**
```bash
# Informações básicas da API
curl http://arcanun-tech.vps-kinghost.net/ | jq .

# Resposta esperada:
# {
#   "message": "🎯 API de Reconhecimento Facial",
#   "version": "2.0.0",
#   "status": "🟢 Online",
#   "endpoints": {
#     "health": "/health",
#     "api": "/api/v1",
#     "statistics": "/api/v1/statistics"
#   }
# }
```

### **4. Health Check**
```bash
# Verificar saúde da API
curl http://arcanun-tech.vps-kinghost.net/health | jq .

# Health check específico da API facial
curl http://arcanun-tech.vps-kinghost.net/api/v1/health | jq .
```

### **5. Listar Todas as Rotas (Método Manual)**
```bash
# Testar endpoints conhecidos
echo "=== TESTANDO ROTAS DA API FACIAL ==="

# Endpoint raiz
echo "1. Endpoint raiz:"
curl -s http://arcanun-tech.vps-kinghost.net/ | jq -r '.message // "Erro"'

# Health checks
echo "2. Health check global:"
curl -s http://arcanun-tech.vps-kinghost.net/health | jq -r '.status // "Erro"'

echo "3. Health check API:"
curl -s http://arcanun-tech.vps-kinghost.net/api/v1/health | jq -r '.status // "Erro"'

# Documentação
echo "4. Documentação (Swagger):"
curl -s -o /dev/null -w "%{http_code}" http://arcanun-tech.vps-kinghost.net/docs

# Estatísticas
echo "5. Estatísticas:"
curl -s http://arcanun-tech.vps-kinghost.net/api/v1/statistics | jq -r '.total_employees // "Erro"'

# Informações do serviço
echo "6. Informações do serviço:"
curl -s http://arcanun-tech.vps-kinghost.net/api/v1/service-info | jq -r '.service_mode // "Erro"'
```

---

## 🔧 Para API Laravel (Sistema de Ponto)

### **1. Comando Artisan (Acesso SSH)**
```bash
# Conectar via SSH no servidor
ssh usuario@diasadvogado.com.br

# Navegar para o diretório do projeto
cd /var/www/ponto  # ou caminho correto

# Listar todas as rotas
php artisan route:list

# Filtrar rotas da API
php artisan route:list --path=api

# Rotas específicas (auth)
php artisan route:list | grep auth

# Salvar em arquivo
php artisan route:list > rotas-disponiveis.txt
```

### **2. Teste via cURL (Sem SSH)**
```bash
# Testar endpoint de login
curl -X POST https://diasadvogado.com.br/ponto/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"email":"teste@teste.com","password":"senha123"}' \
  -v

# Testar outros endpoints comuns
echo "=== TESTANDO ROTAS LARAVEL ==="

# Health check (se existir)
curl -s https://diasadvogado.com.br/ponto/api/health

# Rota raiz da API
curl -s https://diasadvogado.com.br/ponto/api/

# Documentação (se existir)
curl -s https://diasadvogado.com.br/ponto/api/docs
```

### **3. Descobrir Rotas por Tentativa e Erro**
```bash
#!/bin/bash
# Script para descobrir rotas comuns

BASE_URL="https://diasadvogado.com.br/ponto/api"

echo "=== DESCOBRINDO ROTAS LARAVEL ==="

# Lista de endpoints comuns para testar
ENDPOINTS=(
    "/"
    "/health"
    "/status"
    "/docs"
    "/auth/login"
    "/auth/register"
    "/auth/logout"
    "/auth/refresh"
    "/auth/me"
    "/user"
    "/users"
    "/employees"
    "/attendance"
    "/reports"
    "/facial"
    "/facial/validate"
    "/facial/register"
)

for endpoint in "${ENDPOINTS[@]}"; do
    echo -n "Testando $endpoint: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    case $status in
        200) echo "✅ OK ($status)" ;;
        201) echo "✅ Created ($status)" ;;
        401) echo "🔐 Unauthorized ($status) - Rota existe, precisa auth" ;;
        403) echo "🚫 Forbidden ($status) - Rota existe, sem permissão" ;;
        404) echo "❌ Not Found ($status)" ;;
        405) echo "⚠️ Method Not Allowed ($status) - Rota existe, método errado" ;;
        422) echo "📝 Validation Error ($status) - Rota existe, dados inválidos" ;;
        429) echo "🐌 Rate Limited ($status) - Rota existe, muitas tentativas" ;;
        500) echo "💥 Server Error ($status) - Rota existe, erro interno" ;;
        *) echo "❓ Status $status" ;;
    esac
done
```

---

## 🛠️ Ferramentas Úteis

### **1. HTTPie (Alternativa ao cURL)**
```bash
# Instalar HTTPie
pip install httpie

# Testar API FastAPI
http GET http://arcanun-tech.vps-kinghost.net/
http GET http://arcanun-tech.vps-kinghost.net/docs

# Testar API Laravel
http POST https://diasadvogado.com.br/ponto/api/auth/login \
  email=teste@teste.com password=senha123
```

### **2. Postman/Insomnia**
```bash
# Importar coleção da API FastAPI
# URL: http://arcanun-tech.vps-kinghost.net/openapi.json

# Criar requests para testar:
# GET  http://arcanun-tech.vps-kinghost.net/
# GET  http://arcanun-tech.vps-kinghost.net/health
# GET  http://arcanun-tech.vps-kinghost.net/api/v1/statistics
# POST http://arcanun-tech.vps-kinghost.net/api/v1/verify-face/123
```

### **3. Script de Teste Automatizado**
```bash
#!/bin/bash
# test-all-routes.sh

echo "🔍 TESTANDO TODAS AS ROTAS DISPONÍVEIS"
echo "======================================"

# API de Reconhecimento Facial
echo "\n📸 API DE RECONHECIMENTO FACIAL:"
echo "Base URL: http://arcanun-tech.vps-kinghost.net"

# Função para testar endpoint
test_endpoint() {
    local url=$1
    local description=$2
    
    echo -n "  $description: "
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url")
    
    if [ $status -eq 200 ]; then
        echo "✅ OK"
    elif [ $status -eq 404 ]; then
        echo "❌ Not Found"
    else
        echo "⚠️ Status $status"
    fi
}

# Testar endpoints da API Facial
test_endpoint "http://arcanun-tech.vps-kinghost.net/" "Endpoint raiz"
test_endpoint "http://arcanun-tech.vps-kinghost.net/health" "Health check global"
test_endpoint "http://arcanun-tech.vps-kinghost.net/docs" "Documentação Swagger"
test_endpoint "http://arcanun-tech.vps-kinghost.net/openapi.json" "Schema OpenAPI"
test_endpoint "http://arcanun-tech.vps-kinghost.net/api/v1/health" "Health check API"
test_endpoint "http://arcanun-tech.vps-kinghost.net/api/v1/statistics" "Estatísticas"
test_endpoint "http://arcanun-tech.vps-kinghost.net/api/v1/service-info" "Info do serviço"

# API Laravel
echo "\n🏢 API LARAVEL (Sistema de Ponto):"
echo "Base URL: https://diasadvogado.com.br/ponto/api"

test_endpoint "https://diasadvogado.com.br/ponto/api/" "Endpoint raiz"
test_endpoint "https://diasadvogado.com.br/ponto/api/health" "Health check"
test_endpoint "https://diasadvogado.com.br/ponto/api/docs" "Documentação"

echo "\n🔐 Endpoints que precisam de dados:"
echo "  Login: POST https://diasadvogado.com.br/ponto/api/auth/login"
echo "  Facial: POST http://arcanun-tech.vps-kinghost.net/api/v1/verify-face/{id}"

echo "\n✅ Teste concluído!"
```

---

## 📋 Rotas Conhecidas

### **🎯 API de Reconhecimento Facial**
```
GET  /                                    # Informações da API
GET  /health                              # Health check global
GET  /docs                                # Documentação Swagger
GET  /openapi.json                        # Schema OpenAPI
GET  /api/v1/health                       # Health check da API
GET  /api/v1/statistics                   # Estatísticas do sistema
GET  /api/v1/service-info                 # Informações do serviço
GET  /api/v1/employee/{id}/status         # Status do funcionário
POST /api/v1/register-employee/{id}       # Registrar funcionário
POST /api/v1/verify-face/{id}             # Verificar identidade
PUT  /api/v1/update-employee/{id}         # Atualizar foto
DELETE /api/v1/employee/{id}              # Remover funcionário
```

### **🏢 API Laravel (Estimadas)**
```
POST /api/auth/login                      # Login
POST /api/auth/logout                     # Logout
POST /api/auth/refresh                    # Refresh token
GET  /api/auth/me                         # Dados do usuário
GET  /api/employees                       # Listar funcionários
POST /api/attendance                      # Registrar ponto
GET  /api/reports                         # Relatórios
```

---

## 🚀 Comandos Rápidos

### **Testar API Facial:**
```bash
# Informações básicas
curl http://arcanun-tech.vps-kinghost.net/ | jq .

# Ver documentação no navegador
open http://arcanun-tech.vps-kinghost.net/docs
```

### **Testar API Laravel:**
```bash
# Via SSH (se tiver acesso)
ssh usuario@diasadvogado.com.br "cd /var/www/ponto && php artisan route:list"

# Via cURL (descobrir rotas)
curl -X POST https://diasadvogado.com.br/ponto/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"teste","password":"teste"}' -v
```

### **Salvar Resultados:**
```bash
# Salvar schema da API Facial
curl http://arcanun-tech.vps-kinghost.net/openapi.json > api-facial-schema.json

# Salvar rotas do Laravel (via SSH)
php artisan route:list > rotas-laravel.txt
```

---

## ✅ Checklist de Teste

- [ ] ✅ Testar endpoint raiz da API Facial
- [ ] ✅ Verificar documentação Swagger
- [ ] ✅ Testar health checks
- [ ] ✅ Baixar schema OpenAPI
- [ ] ✅ Testar login do Laravel
- [ ] ✅ Listar rotas via SSH (se possível)
- [ ] ✅ Documentar rotas encontradas
- [ ] ✅ Criar coleção no Postman

**Agora você pode descobrir todas as rotas disponíveis nos seus servidores!** 🎯