# 🔍 Testes de Diagnóstico - Conexão API Facial

## ❌ Problema Atual
O Flutter está tentando conectar em `http://arcanun-tech.vps-kinghost.net:8000/api/compare` e recebendo "Connection refused".

## 🎯 Objetivo dos Testes
Verificar se:
1. A API está rodando na porta 8000
2. O Nginx está funcionando na porta 80
3. O proxy reverso está configurado corretamente
4. A rota `/api/compare` está acessível

---

## 🧪 Testes para Executar no Servidor

### 1. **Verificar se a API está rodando**
```bash
# Verificar processos na porta 8000
sudo netstat -tlnp | grep :8000

# Verificar se a API responde localmente
curl -X GET http://127.0.0.1:8000/

# Testar a rota compare localmente
curl -X POST http://127.0.0.1:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'
```

### 2. **Verificar se o Nginx está funcionando**
```bash
# Status do Nginx
sudo systemctl status nginx

# Verificar se está escutando na porta 80
sudo netstat -tlnp | grep :80

# Testar Nginx localmente
curl -X GET http://127.0.0.1/

# Testar health check do Nginx
curl -X GET http://127.0.0.1/nginx-health
```

### 3. **Testar o proxy reverso**
```bash
# Testar a rota compare via Nginx
curl -X POST http://127.0.0.1/api/compare \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'

# Verificar logs do Nginx
sudo tail -f /var/log/nginx/api_compare.log
sudo tail -f /var/log/nginx/api_access.log
sudo tail -f /var/log/nginx/api_error.log
```

### 4. **Testar externamente**
```bash
# Do seu computador local, testar:
curl -X GET http://arcanun-tech.vps-kinghost.net/
curl -X GET http://arcanun-tech.vps-kinghost.net/nginx-health

# Testar a rota compare externamente
curl -X POST http://arcanun-tech.vps-kinghost.net/api/compare \
  -H "Content-Type: application/json" \
  -d '{"test": "true"}'
```

---

## 🔧 Comandos de Diagnóstico

### **Verificar configuração do Nginx**
```bash
# Testar configuração
sudo nginx -t

# Ver configuração ativa
sudo nginx -T | grep -A 20 "location /api/compare"

# Recarregar se necessário
sudo nginx -s reload
```

### **Verificar se a API está rodando**
```bash
# Verificar serviço da API
sudo systemctl status facial-api

# Ver logs da API
sudo journalctl -u facial-api -f

# Verificar processos Python
ps aux | grep python
ps aux | grep gunicorn
ps aux | grep uvicorn
```

### **Verificar firewall**
```bash
# Status do firewall
sudo ufw status

# Verificar se as portas estão abertas
sudo ufw status numbered

# Se necessário, abrir portas
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
```

---

## 📊 Resultados Esperados

### ✅ **Se tudo estiver funcionando:**
1. **Porta 8000**: API responde localmente
2. **Porta 80**: Nginx responde
3. **Proxy**: `/api/compare` via Nginx funciona
4. **Externo**: Acesso via domínio funciona

### ❌ **Possíveis problemas:**

#### **API não está rodando (porta 8000)**
```bash
# Iniciar a API
sudo systemctl start facial-api
sudo systemctl enable facial-api

# Ou manualmente
cd /path/to/api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### **Nginx não está rodando**
```bash
# Iniciar Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### **Configuração do Nginx incorreta**
```bash
# Aplicar a configuração corrigida
sudo cp nginx.conf /etc/nginx/nginx.conf
sudo nginx -t
sudo nginx -s reload
```

#### **Firewall bloqueando**
```bash
# Abrir portas necessárias
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw reload
```

---

## 🎯 Correção para o Flutter

### **Problema identificado:**
O Flutter está tentando conectar diretamente na porta 8000, mas deveria usar a porta 80 (Nginx).

### **Solução:**
Alterar a URL no código Laravel/Flutter de:
```
http://arcanun-tech.vps-kinghost.net:8000/api/compare
```

Para:
```
http://arcanun-tech.vps-kinghost.net/api/compare
```

### **Configuração no Laravel (.env):**
```env
FACE_MICROSERVICE_URL=http://arcanun-tech.vps-kinghost.net
FACE_MICROSERVICE_TIMEOUT=120
```

---

## 📝 Checklist de Verificação

- [ ] API rodando na porta 8000
- [ ] Nginx rodando na porta 80
- [ ] Configuração do Nginx aplicada
- [ ] Proxy reverso funcionando
- [ ] Firewall configurado
- [ ] URL no Laravel/Flutter corrigida
- [ ] Teste externo funcionando

---

## 🚀 Próximos Passos

1. **Execute os testes na ordem**
2. **Identifique onde está o problema**
3. **Aplique a correção correspondente**
4. **Atualize a URL no código do Flutter/Laravel**
5. **Teste novamente**

**Resultado esperado:** Flutter conectando com sucesso via `http://arcanun-tech.vps-kinghost.net/api/compare`