# 🔧 Configuração Nginx para Rota `/api/compare`

## 🚨 Problema Identificado

O erro que você está recebendo:
```
cURL error 7: Failed to connect to arcanun-tech.vps-kinghost.net port 8000: Connection refused
```

Indica que o **nginx não está configurado** para fazer proxy reverso da rota `/api/compare` para a aplicação que roda na porta 8000.

## 📋 Análise da Configuração Atual

Sua configuração nginx atual:
- ✅ Está configurada para `/api/v1/*` (FastAPI)
- ❌ **NÃO** está configurada para `/api/compare` (Flask/API direta)
- ✅ Upstream aponta para `facial-api:8000`
- ❌ Falta configuração específica para `/api/compare`

## 🔧 Solução: Adicionar Configuração para `/api/compare`

### **1. Atualizar nginx.conf**

Adicione esta configuração no bloco `server` (após a linha 95, antes de `location /`):

```nginx
# Configuração específica para /api/compare (API direta)
location /api/compare {
    limit_req zone=upload burst=5 nodelay;
    proxy_pass http://facial_api;
    
    # Headers específicos para API de comparação
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_set_header Content-Type application/json;
    
    # Timeouts maiores para processamento de imagens
    proxy_connect_timeout 30s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
    
    # Permitir métodos HTTP necessários
    proxy_method POST;
    
    # Log específico para debug
    access_log /var/log/nginx/api_compare.log api_access;
}
```

### **2. Configuração Completa Atualizada**

Aqui está a seção completa do servidor com a nova configuração:

```nginx
# Servidor principal
server {
    listen 80;
    server_name _;  # Substitua pelo seu domínio
    
    # Logs
    access_log /var/log/nginx/api_access.log api_access;
    error_log /var/log/nginx/api_error.log warn;
    
    # Timeout configurations
    proxy_connect_timeout 30s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
    
    # Headers para proxy
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Health check do Nginx
    location /nginx-health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # 🆕 NOVA CONFIGURAÇÃO: /api/compare
    location /api/compare {
        limit_req zone=upload burst=5 nodelay;
        proxy_pass http://facial_api;
        
        # Timeouts maiores para processamento de imagens
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        
        # Log específico para debug
        access_log /var/log/nginx/api_compare.log api_access;
    }
    
    # Endpoints da API com rate limiting normal
    location /api/v1 {
        limit_req zone=api burst=10 nodelay;
        proxy_pass http://facial_api;
    }
    
    # Endpoints de upload com rate limiting específico
    location ~ ^/api/v1/(register-employee|verify-face|update-employee) {
        limit_req zone=upload burst=5 nodelay;
        proxy_pass http://facial_api;
        
        # Timeouts maiores para uploads
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
    }
    
    # Documentação e interface
    location ~ ^/(docs|redoc|openapi\.json) {
        proxy_pass http://facial_api;
    }
    
    # Health checks
    location /health {
        access_log off;
        proxy_pass http://facial_api;
    }
    
    # Endpoint raiz
    location / {
        proxy_pass http://facial_api;
    }
    
    # ... resto da configuração
}
```

## 🚀 Comandos para Aplicar a Configuração

### **1. Editar o arquivo nginx.conf no servidor:**
```bash
# Conectar ao servidor
ssh usuario@arcanun-tech.vps-kinghost.net

# Editar configuração do nginx
sudo nano /etc/nginx/nginx.conf
# ou se estiver usando Docker:
sudo docker exec -it nginx_container nano /etc/nginx/nginx.conf
```

### **2. Testar a configuração:**
```bash
# Testar sintaxe do nginx
sudo nginx -t

# Se estiver usando Docker:
sudo docker exec nginx_container nginx -t
```

### **3. Recarregar o nginx:**
```bash
# Recarregar configuração
sudo nginx -s reload

# Se estiver usando Docker:
sudo docker exec nginx_container nginx -s reload

# Ou reiniciar o container:
sudo docker restart nginx_container
```

## 🧪 Testar a Configuração

### **1. Teste direto no servidor:**
```bash
# Testar se o nginx está redirecionando corretamente
curl -X POST http://localhost/api/compare \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'

# Deve retornar erro de campos obrigatórios, não erro de conexão
```

### **2. Teste externo:**
```bash
# Do seu computador local
curl -X POST http://arcanun-tech.vps-kinghost.net/api/compare \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'
```

### **3. Teste com dados válidos:**
```bash
curl -X POST http://arcanun-tech.vps-kinghost.net/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "reference_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "captured_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "employee_id": "123"
  }'
```

## 🔍 Debug e Monitoramento

### **1. Verificar logs do nginx:**
```bash
# Log geral
sudo tail -f /var/log/nginx/api_access.log

# Log específico do /api/compare (se configurado)
sudo tail -f /var/log/nginx/api_compare.log

# Log de erros
sudo tail -f /var/log/nginx/api_error.log
```

### **2. Verificar se a aplicação está rodando:**
```bash
# Verificar se a aplicação está na porta 8000
sudo netstat -tlnp | grep :8000

# Ou com ss
sudo ss -tlnp | grep :8000

# Testar diretamente na porta 8000 (bypass nginx)
curl http://localhost:8000/api/compare
```

### **3. Verificar status do container (se usando Docker):**
```bash
# Listar containers
sudo docker ps

# Verificar logs da aplicação
sudo docker logs facial-api

# Verificar logs do nginx
sudo docker logs nginx_container
```

## 🎯 Configuração Alternativa (Se Necessário)

Se a configuração acima não funcionar, tente esta alternativa mais específica:

```nginx
# Configuração alternativa para /api/compare
location = /api/compare {
    # Permitir apenas POST
    limit_except POST {
        deny all;
    }
    
    limit_req zone=upload burst=5 nodelay;
    
    # Proxy para a aplicação
    proxy_pass http://127.0.0.1:8000/api/compare;
    
    # Headers necessários
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Configurações para upload de imagens
    client_max_body_size 20M;
    proxy_request_buffering off;
    
    # Timeouts
    proxy_connect_timeout 30s;
    proxy_send_timeout 120s;
    proxy_read_timeout 120s;
}
```

## ✅ Checklist de Verificação

- [ ] Configuração `/api/compare` adicionada ao nginx.conf
- [ ] Sintaxe do nginx testada (`nginx -t`)
- [ ] Nginx recarregado (`nginx -s reload`)
- [ ] Aplicação rodando na porta 8000
- [ ] Teste local funcionando
- [ ] Teste externo funcionando
- [ ] Logs do nginx sem erros
- [ ] Laravel consegue conectar na API

## 🎯 Resultado Esperado

Após aplicar essas configurações:

✅ **Antes**: `Connection refused` na porta 8000  
✅ **Depois**: Nginx faz proxy para `/api/compare` → aplicação na porta 8000

Seu Laravel deve conseguir conectar em:
`https://diasadvogado.com.br/ponto/api/face-validation/compare-with-microservice`

Que internamente chama:
`http://arcanun-tech.vps-kinghost.net/api/compare` (via nginx proxy)

Que redireciona para:
`http://localhost:8000/api/compare` (aplicação real)