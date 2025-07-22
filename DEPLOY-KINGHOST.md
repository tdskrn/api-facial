# 🚀 Guia Completo de Deploy na KingHost VPS

## 📋 Pré-requisitos

### **VPS KingHost Recomendada**
- **Plano**: VPS Cloud 4GB RAM ou superior
- **Sistema**: Ubuntu 20.04 LTS ou 22.04 LTS
- **Recursos mínimos**: 2 vCPU, 4GB RAM, 40GB SSD
- **Acesso**: SSH root habilitado

### **Domínio e DNS**
- Domínio apontando para o IP da VPS
- Subdomínio recomendado: `api-facial.seudominio.com.br`

---

## 🔧 Passo 1: Preparação do Servidor

### **1.1 Conectar via SSH**
```bash
ssh root@SEU_IP_VPS
```

### **1.2 Atualizar o Sistema**
```bash
apt update && apt upgrade -y
apt install -y curl wget git nano htop unzip
```

### **1.3 Criar Usuário para a Aplicação**
```bash
# Criar usuário
adduser facial-api
usermod -aG sudo facial-api

# Configurar SSH para o novo usuário
mkdir -p /home/facial-api/.ssh
cp ~/.ssh/authorized_keys /home/facial-api/.ssh/
chown -R facial-api:facial-api /home/facial-api/.ssh
chmod 700 /home/facial-api/.ssh
chmod 600 /home/facial-api/.ssh/authorized_keys
```

### **1.4 Configurar Firewall**
```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable
```

---

## 🐍 Passo 2: Instalar Python e Dependências

### **2.1 Instalar Python 3.10+**
```bash
apt install -y python3 python3-pip python3-venv python3-dev
apt install -y build-essential cmake libopenblas-dev liblapack-dev
apt install -y libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev
apt install -y libgomp1 libx11-dev libgtk-3-dev
```

### **2.2 Verificar Versão do Python**
```bash
python3 --version  # Deve ser 3.8+ (recomendado 3.10+)
```

---

## 📁 Passo 3: Deploy da Aplicação

### **3.1 Mudar para o Usuário da Aplicação**
```bash
su - facial-api
```

### **3.2 Clonar o Repositório**
```bash
cd /home/facial-api
git clone https://github.com/SEU_USUARIO/api-facial.git
cd api-facial
```

### **3.3 Criar Ambiente Virtual**
```bash
python3 -m venv venv
source venv/bin/activate
```

### **3.4 Instalar Dependências**
```bash
# Atualizar pip
pip install --upgrade pip

# Instalar dependências básicas
pip install -r requirements.txt

# Para funcionalidade completa de reconhecimento facial
pip install face-recognition opencv-python-headless numpy Pillow
```

### **3.5 Configurar Variáveis de Ambiente**
```bash
cp .env.example .env
nano .env
```

**Configuração do arquivo `.env`:**
```env
# Configurações básicas
DEBUG=false
SECRET_KEY=SUA_CHAVE_SECRETA_SUPER_FORTE_AQUI_123456789
PORT=8000
ENVIRONMENT=production

# Integração com Laravel (OBRIGATÓRIO)
LARAVEL_API_BASE=https://seu-site-laravel.com.br
LARAVEL_API_TOKEN=seu-token-bearer-aqui

# Reconhecimento facial
FACE_TOLERANCE=0.6
MAX_FILE_SIZE=10485760

# Logs
LOG_LEVEL=INFO
```

### **3.6 Criar Diretórios Necessários**
```bash
mkdir -p logs
mkdir -p app/storage/employee_photos
mkdir -p app/storage/temp
chmod 755 logs app/storage
```

### **3.7 Testar a Aplicação**
```bash
# Ativar ambiente virtual
source venv/bin/activate

# Testar se a aplicação inicia
python app.py
```

**Se tudo estiver OK, você verá:**
```
🚀 Iniciando API de Reconhecimento Facial
🌐 Laravel API: https://seu-site-laravel.com.br
🔐 Token configurado: Sim
🔧 Debug mode: False
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```

**Pressione `Ctrl+C` para parar e continuar.**

---

## 🔧 Passo 4: Configurar Gunicorn

### **4.1 Testar Gunicorn**
```bash
source venv/bin/activate
gunicorn --config gunicorn.conf.py app:app
```

**Se funcionar, pressione `Ctrl+C` e continue.**

---

## 🔄 Passo 5: Configurar Systemd Service

### **5.1 Voltar para Root**
```bash
exit  # Sair do usuário facial-api
```

### **5.2 Criar Service File**
```bash
nano /etc/systemd/system/facial-api.service
```

**Conteúdo do arquivo:**
```ini
[Unit]
Description=🧠 API de Reconhecimento Facial para Ponto Eletrônico
After=network.target
Wants=network.target

[Service]
Type=notify
User=facial-api
Group=facial-api
WorkingDirectory=/home/facial-api/api-facial
Environment=PATH=/home/facial-api/api-facial/venv/bin
EnvironmentFile=/home/facial-api/api-facial/.env
ExecStart=/home/facial-api/api-facial/venv/bin/gunicorn --config gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

### **5.3 Habilitar e Iniciar o Service**
```bash
systemctl daemon-reload
systemctl enable facial-api
systemctl start facial-api
systemctl status facial-api
```

**Verificar se está rodando:**
```bash
curl http://localhost:8000/health
```

---

## 🌐 Passo 6: Configurar Nginx

### **6.1 Instalar Nginx**
```bash
apt install -y nginx
```

### **6.2 Criar Configuração do Site**
```bash
nano /etc/nginx/sites-available/facial-api
```

**Conteúdo do arquivo:**
```nginx
server {
    listen 80;
    server_name api-facial.seudominio.com.br;
    
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
    
    # Arquivos estáticos (se houver)
    location /static/ {
        alias /home/facial-api/api-facial/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        access_log off;
    }
}
```

### **6.3 Habilitar o Site**
```bash
ln -s /etc/nginx/sites-available/facial-api /etc/nginx/sites-enabled/
nginx -t  # Testar configuração
systemctl restart nginx
```

---

## 🔒 Passo 7: Configurar SSL com Let's Encrypt

### **7.1 Instalar Certbot**
```bash
apt install -y certbot python3-certbot-nginx
```

### **7.2 Obter Certificado SSL**
```bash
certbot --nginx -d api-facial.seudominio.com.br
```

**Siga as instruções do certbot.**

### **7.3 Configurar Renovação Automática**
```bash
crontab -e
```

**Adicionar linha:**
```
0 12 * * * /usr/bin/certbot renew --quiet
```

---

## ✅ Passo 8: Verificação Final

### **8.1 Testar a API**
```bash
# Teste básico
curl https://api-facial.seudominio.com.br/health

# Teste de upload (substitua pelo caminho de uma foto)
curl -X POST -F "photo=@/caminho/para/foto.jpg" \
     https://api-facial.seudominio.com.br/api/validate
```

### **8.2 Verificar Logs**
```bash
# Logs da aplicação
tail -f /home/facial-api/api-facial/logs/api.log

# Logs do systemd
journalctl -u facial-api -f

# Logs do Nginx
tail -f /var/log/nginx/facial-api.access.log
```

### **8.3 Verificar Status dos Serviços**
```bash
systemctl status facial-api
systemctl status nginx
```

---

## 🔧 Comandos Úteis para Manutenção

### **Reiniciar Aplicação**
```bash
sudo systemctl restart facial-api
```

### **Ver Logs em Tempo Real**
```bash
sudo journalctl -u facial-api -f
```

### **Atualizar Código**
```bash
su - facial-api
cd api-facial
git pull
source venv/bin/activate
pip install -r requirements.txt
exit
sudo systemctl restart facial-api
```

### **Backup dos Dados**
```bash
tar -czf backup-facial-api-$(date +%Y%m%d).tar.gz \
    /home/facial-api/api-facial/app/storage \
    /home/facial-api/api-facial/.env \
    /home/facial-api/api-facial/logs
```

---

## 🚨 Solução de Problemas

### **Problema: Aplicação não inicia**
```bash
# Verificar logs
journalctl -u facial-api -n 50

# Verificar se o Python está funcionando
su - facial-api
cd api-facial
source venv/bin/activate
python app.py
```

### **Problema: Erro de dependências**
```bash
su - facial-api
cd api-facial
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### **Problema: Nginx não consegue conectar**
```bash
# Verificar se a aplicação está rodando na porta 8000
netstat -tlnp | grep 8000

# Verificar configuração do Nginx
nginx -t
```

### **Problema: Upload de arquivos falha**
```bash
# Verificar permissões
chown -R facial-api:facial-api /home/facial-api/api-facial/app/storage
chmod -R 755 /home/facial-api/api-facial/app/storage
```

---

## 📊 Monitoramento

### **Verificar Uso de Recursos**
```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Logs de tamanho
du -sh /home/facial-api/api-facial/logs/*
```

### **Limpar Logs Antigos**
```bash
# Manter apenas últimos 7 dias
find /home/facial-api/api-facial/logs -name "*.log" -mtime +7 -delete
```

---

## 🎯 Próximos Passos

1. **Configurar backup automático** dos dados
2. **Implementar monitoramento** com alertas
3. **Configurar rate limiting** no Nginx
4. **Implementar cache** para melhor performance
5. **Configurar logs estruturados** para análise

---

## 📞 Suporte

Se encontrar problemas:

1. Verifique os logs: `journalctl -u facial-api -f`
2. Teste a conectividade: `curl http://localhost:8000/health`
3. Verifique as permissões dos arquivos
4. Consulte a documentação da KingHost

**🎉 Parabéns! Sua API de Reconhecimento Facial está rodando na KingHost!**

---

*Última atualização: $(date +%Y-%m-%d)*