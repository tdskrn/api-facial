# 🚀 Migração para Flask - API de Reconhecimento Facial

## 📌 Resumo da Migração

O projeto foi migrado de **FastAPI + Docker** para **Flask + VPS** seguindo suas especificações para deploy na KingHost.

## 🔄 Principais Mudanças

### Arquitetura
- ✅ **Antes**: FastAPI + aiofiles + local file storage
- ✅ **Agora**: Flask + requests + URL-based image storage

### Deployment
- ✅ **Antes**: Docker + docker-compose
- ✅ **Agora**: VPS direct deployment + systemd + nginx

### API Endpoints
- ✅ **Antes**: Multiple RESTful endpoints (`/register-employee/{id}`, `/verify-face/{id}`)
- ✅ **Agora**: Single validation endpoint (`/api/validate`)

### Storage Pattern
- ✅ **Antes**: Local files em `app/storage/employee_photos/`
- ✅ **Agora**: URLs como `https://seudominio.com/storage/funcionarios/{id}.jpg`

## 📁 Novos Arquivos

### Core Flask Application
- `app.py` - Aplicação Flask principal
- `utils/face_matcher.py` - Módulo de reconhecimento facial com URLs
- `requirements-flask.txt` - Dependências Flask

### Deployment & Production
- `deploy-kinghost.sh` - Script de deploy para VPS KingHost
- `gunicorn.conf.py` - Configuração do Gunicorn otimizada
- `nginx-flask.conf` - Configuração Nginx para reverse proxy
- `facial-api.service` - Arquivo systemd service

### Testing
- `test-flask.py` - Script de testes para API Flask

## 🎯 Como Usar

### Desenvolvimento Local
```bash
# Instalar dependências
pip install -r requirements-flask.txt

# Configurar variáveis
cp .env.example .env
# Editar BASE_URL no .env

# Executar
python3 app.py
```

### Deploy VPS KingHost
```bash
# Dar permissão
chmod +x deploy-kinghost.sh

# Deploy completo
./deploy-kinghost.sh install

# Atualizar código
./deploy-kinghost.sh update
```

### Testar API
```bash
# Testar endpoints
python3 test-flask.py

# Health check manual
curl http://localhost:8000/health

# Testar validação
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{"employee_id": "123", "image_base64": "data:image/jpeg;base64,..."}'
```

## 🔧 Configuração Required

### 1. Arquivo .env
```bash
BASE_URL=https://seudominio.com/storage/funcionarios
SECRET_KEY=sua-chave-secreta-forte
DEBUG=false
```

### 2. Nginx Domain
Editar `nginx-flask.conf` e alterar:
```nginx
server_name sua-api.com www.sua-api.com;
```

### 3. SSL (Recomendado)
```bash
# Instalar certbot
sudo apt install certbot python3-certbot-nginx

# Gerar certificado
sudo certbot --nginx -d sua-api.com
```

## 📊 Performance Otimizada

### VPS KingHost 4GB RAM
- **Workers**: 4 (otimizado para 4GB)
- **Timeout**: 60s (reconhecimento facial)
- **Max requests**: 500 (recicla workers)
- **Rate limiting**: 30 req/min (API), 10 req/min (upload)

### Nginx Optimizations
- **Proxy timeout**: 60s
- **Client max body**: 10MB
- **Gzip compression**: Ativada
- **Security headers**: Configurados

## 🧪 Testes Incluídos

### Automatizados (`test-flask.py`)
- ✅ Health check
- ✅ Endpoint raiz
- ✅ Validação com imagem mock
- ✅ Testes de erro (JSON inválido, campos faltando)
- ✅ Endpoint 404

### Manuais
```bash
# Health check
curl http://localhost:8000/health

# Info da API
curl http://localhost:8000/

# Status do serviço
sudo systemctl status facial-api
```

## 📚 Arquivos Legacy (Mantidos)

Os arquivos FastAPI/Docker foram mantidos como fallback:
- `app/` - Estrutura FastAPI original
- `docker-compose.yml` - Configuração Docker
- `deploy.sh` - Script Docker deploy
- `requirements.txt` - Dependências FastAPI

Para usar a versão legacy:
```bash
# Docker
./deploy.sh production

# Python direto
cd app && python3 main.py
```

## 🎉 Benefícios da Migração

### ✅ Simplicidade
- Menos dependências (sem Docker)
- Deploy direto no VPS
- Configuração mais simples

### ✅ Performance
- Sem overhead do Docker
- Otimizado para VPS KingHost
- Nginx como reverse proxy

### ✅ Manutenção
- Logs centralizados
- Systemd integration
- Auto-restart em caso de falha

### ✅ Custo
- Sem necessidade de recursos Docker
- Mais eficiente uso da RAM
- Deploy mais rápido

## 🔍 Próximos Passos

1. **Configurar domínio** na KingHost
2. **Editar nginx-flask.conf** com seu domínio
3. **Configurar SSL** com Let's Encrypt
4. **Ajustar BASE_URL** no .env
5. **Testar integração** com Laravel backend
6. **Configurar monitoring** (opcional)

## 🆘 Troubleshooting

### API não responde
```bash
sudo systemctl status facial-api
sudo journalctl -u facial-api -f
```

### Nginx erro
```bash
sudo nginx -t
sudo systemctl status nginx
tail -f /var/log/nginx/facial-api-error.log
```

### Face recognition erro
```bash
# Verificar dependências
python3 -c "import face_recognition; print('OK')"
```

### Logs da aplicação
```bash
tail -f /var/www/facial-api/logs/api.log
```