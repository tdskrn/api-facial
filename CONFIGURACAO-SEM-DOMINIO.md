# 🌐 Configuração sem Domínio Personalizado - KingHost VPS

## 📋 Sua Situação

- **Endereço VPS**: `arcanun-tech.vps-kinghost.net`
- **IP**: `189.126.111.41`
- **Sem domínio personalizado**

---

## 🔧 Configuração do Nginx

### **Passo 1: Editar Configuração do Nginx**

```bash
sudo nano /etc/nginx/sites-available/facial-api
```

### **Passo 2: Configuração Correta**

**Substitua todo o conteúdo por:**

```nginx
server {
    listen 80;
    server_name arcanun-tech.vps-kinghost.net 189.126.111.41;
    
    # Logs
    access_log /var/log/nginx/facial-api.access.log;
    error_log /var/log/nginx/facial-api.error.log;
    
    # Configurações para upload de arquivos
    client_max_body_size 15M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    
    # Proxy para a aplicação
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    # Bloquear acesso a arquivos sensíveis
    location ~ /\.(ht|env) {
        deny all;
    }
}
```

### **Passo 3: Testar e Aplicar**

```bash
# Testar configuração
sudo nginx -t

# Se OK, reiniciar Nginx
sudo systemctl restart nginx

# Verificar status
sudo systemctl status nginx
```

---

## 🧪 Testar a API

### **Teste Local (no servidor)**
```bash
curl http://localhost:8000/health
```

### **Teste Externo**
```bash
# Via endereço da VPS
curl http://arcanun-tech.vps-kinghost.net/health

# Via IP
curl http://189.126.111.41/health
```

### **Teste no Navegador**
Acesse:
- `http://arcanun-tech.vps-kinghost.net/health`
- `http://189.126.111.41/health`

---

## 🔒 SSL sem Domínio Personalizado

### **Opção 1: Certificado Auto-assinado (Desenvolvimento)**

```bash
# Criar certificado auto-assinado
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/facial-api.key \
    -out /etc/ssl/certs/facial-api.crt

# Durante a criação, use:
# Common Name: arcanun-tech.vps-kinghost.net
```

**Configuração Nginx com SSL:**
```nginx
server {
    listen 80;
    server_name arcanun-tech.vps-kinghost.net 189.126.111.41;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name arcanun-tech.vps-kinghost.net 189.126.111.41;
    
    ssl_certificate /etc/ssl/certs/facial-api.crt;
    ssl_certificate_key /etc/ssl/private/facial-api.key;
    
    # Resto da configuração igual...
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **Opção 2: Usar apenas HTTP (Mais Simples)**

Para desenvolvimento/teste, você pode usar apenas HTTP sem SSL.

---

## 📱 URLs de Acesso

### **Endpoints da API:**
- **Health Check**: `http://arcanun-tech.vps-kinghost.net/health`
- **Validação**: `http://arcanun-tech.vps-kinghost.net/api/validate`
- **Documentação**: `http://arcanun-tech.vps-kinghost.net/docs`

### **Teste de Upload:**
```bash
curl -X POST -F "photo=@/caminho/para/foto.jpg" \
     http://arcanun-tech.vps-kinghost.net/api/validate
```

---

## 🔧 Script Automatizado

**Crie um script para facilitar:**

```bash
#!/bin/bash
# configure-nginx-sem-dominio.sh

VPS_ADDRESS="arcanun-tech.vps-kinghost.net"
VPS_IP="189.126.111.41"

echo "🌐 Configurando Nginx para VPS sem domínio personalizado..."

# Backup da configuração atual
sudo cp /etc/nginx/sites-available/facial-api /etc/nginx/sites-available/facial-api.backup

# Criar nova configuração
sudo tee /etc/nginx/sites-available/facial-api > /dev/null <<EOF
server {
    listen 80;
    server_name $VPS_ADDRESS $VPS_IP;
    
    access_log /var/log/nginx/facial-api.access.log;
    error_log /var/log/nginx/facial-api.error.log;
    
    client_max_body_size 15M;
    client_body_timeout 30s;
    client_header_timeout 30s;
    
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
    
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
    
    location ~ /\\.(ht|env) {
        deny all;
    }
}
EOF

# Testar configuração
echo "🧪 Testando configuração do Nginx..."
if sudo nginx -t; then
    echo "✅ Configuração OK"
    sudo systemctl restart nginx
    echo "🔄 Nginx reiniciado"
else
    echo "❌ Erro na configuração"
    sudo cp /etc/nginx/sites-available/facial-api.backup /etc/nginx/sites-available/facial-api
    exit 1
fi

# Testar API
echo "🧪 Testando API..."
sleep 3
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API respondendo localmente"
else
    echo "❌ API não está respondendo"
fi

echo "🎉 Configuração concluída!"
echo "📱 Acesse: http://$VPS_ADDRESS/health"
echo "🌐 Ou via IP: http://$VPS_IP/health"
EOF

# Tornar executável
chmod +x configure-nginx-sem-dominio.sh

# Executar
sudo ./configure-nginx-sem-dominio.sh
```

---

## 🚨 Solução de Problemas

### **Problema: Nginx não reinicia**
```bash
# Verificar erros
sudo nginx -t
sudo systemctl status nginx

# Ver logs
sudo tail -f /var/log/nginx/error.log
```

### **Problema: API não responde externamente**
```bash
# Verificar se a aplicação está rodando
sudo systemctl status facial-api
netstat -tlnp | grep 8000

# Verificar firewall
sudo ufw status
sudo ufw allow 80/tcp
```

### **Problema: Erro 502 Bad Gateway**
```bash
# Verificar se a aplicação está na porta 8000
curl http://localhost:8000/health

# Reiniciar aplicação
sudo systemctl restart facial-api
```

---

## 📊 Monitoramento

### **Verificar Status**
```bash
# Status dos serviços
sudo systemctl status facial-api nginx

# Logs em tempo real
sudo journalctl -u facial-api -f
sudo tail -f /var/log/nginx/facial-api.access.log
```

### **Teste Automatizado**
```bash
#!/bin/bash
# test-api-sem-dominio.sh

VPS_ADDRESS="arcanun-tech.vps-kinghost.net"

echo "🧪 Testando API sem domínio personalizado..."

# Teste local
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API local: OK"
else
    echo "❌ API local: FALHOU"
fi

# Teste externo
if curl -f http://$VPS_ADDRESS/health > /dev/null 2>&1; then
    echo "✅ API externa: OK"
    echo "🌐 URL: http://$VPS_ADDRESS/health"
else
    echo "❌ API externa: FALHOU"
fi
```

---

## 🎯 Próximos Passos

1. **Configurar o Nginx** com o endereço da VPS
2. **Testar a API** nos endpoints
3. **Configurar monitoramento** básico
4. **Documentar URLs** para sua equipe
5. **Considerar domínio personalizado** no futuro

---

## 💡 Dica para o Futuro

Quando você adquirir um domínio personalizado:

1. **Aponte o domínio** para o IP `189.126.111.41`
2. **Edite o Nginx** substituindo `arcanun-tech.vps-kinghost.net` pelo seu domínio
3. **Configure SSL** com Let's Encrypt
4. **Atualize sua aplicação Laravel** com a nova URL

---

**🎉 Sua API está configurada para funcionar sem domínio personalizado!**

*Use o endereço `arcanun-tech.vps-kinghost.net` para acessar sua API de reconhecimento facial.*