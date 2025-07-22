# 🔧 Troubleshooting e Manutenção - KingHost VPS

## 🚨 Problemas Comuns e Soluções

### **1. Aplicação não inicia**

#### **Sintomas:**
- `systemctl status facial-api` mostra "failed"
- Erro 502 Bad Gateway no navegador
- API não responde em localhost:8000

#### **Diagnóstico:**
```bash
# Verificar logs do serviço
journalctl -u facial-api -n 50

# Verificar se o processo está rodando
ps aux | grep gunicorn

# Verificar portas em uso
netstat -tlnp | grep 8000
```

#### **Soluções:**
```bash
# 1. Reiniciar o serviço
sudo systemctl restart facial-api

# 2. Verificar configuração do ambiente
su - facial-api
cd api-facial
source venv/bin/activate
python app.py  # Testar manualmente

# 3. Verificar dependências
pip install -r requirements.txt --force-reinstall

# 4. Verificar permissões
sudo chown -R facial-api:facial-api /home/facial-api/api-facial
sudo chmod -R 755 /home/facial-api/api-facial
```

---

### **2. Erro de Dependências Python**

#### **Sintomas:**
- `ModuleNotFoundError`
- `ImportError`
- Aplicação falha ao importar bibliotecas

#### **Soluções:**
```bash
# Entrar no ambiente da aplicação
su - facial-api
cd api-facial
source venv/bin/activate

# Verificar versão do Python
python --version

# Reinstalar dependências
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall

# Para problemas com face_recognition
sudo apt install -y cmake build-essential
pip install dlib
pip install face-recognition

# Para problemas com OpenCV
pip uninstall opencv-python opencv-python-headless
pip install opencv-python-headless
```

---

### **3. Problemas de Upload de Arquivos**

#### **Sintomas:**
- Erro 413 (Payload Too Large)
- Upload falha silenciosamente
- Erro de permissão ao salvar arquivos

#### **Soluções:**
```bash
# 1. Verificar configuração do Nginx
sudo nano /etc/nginx/sites-available/facial-api
# Verificar se tem: client_max_body_size 15M;

# 2. Verificar permissões dos diretórios
sudo chown -R facial-api:facial-api /home/facial-api/api-facial/app/storage
sudo chmod -R 755 /home/facial-api/api-facial/app/storage

# 3. Criar diretórios se não existirem
su - facial-api
cd api-facial
mkdir -p app/storage/employee_photos
mkdir -p app/storage/temp

# 4. Reiniciar serviços
sudo systemctl restart nginx
sudo systemctl restart facial-api
```

---

### **4. Problemas de SSL/HTTPS**

#### **Sintomas:**
- Certificado expirado
- Erro de conexão segura
- Mixed content warnings

#### **Soluções:**
```bash
# 1. Verificar status do certificado
sudo certbot certificates

# 2. Renovar certificado manualmente
sudo certbot renew

# 3. Reconfigurar SSL
sudo certbot --nginx -d seu-dominio.com.br

# 4. Verificar configuração do Nginx
sudo nginx -t
sudo systemctl reload nginx

# 5. Verificar cron de renovação
sudo crontab -l | grep certbot
```

---

### **5. Alto Uso de CPU/Memória**

#### **Diagnóstico:**
```bash
# Monitorar recursos
htop

# Verificar uso por processo
ps aux --sort=-%cpu | head -10
ps aux --sort=-%mem | head -10

# Verificar logs de erro
tail -f /home/facial-api/api-facial/logs/api.log
journalctl -u facial-api -f
```

#### **Soluções:**
```bash
# 1. Ajustar configuração do Gunicorn
su - facial-api
cd api-facial
nano gunicorn.conf.py
# Reduzir workers se necessário

# 2. Limpar logs antigos
sudo find /home/facial-api/api-facial/logs -name "*.log" -mtime +7 -delete
sudo find /var/log/nginx -name "*.log" -mtime +7 -delete

# 3. Reiniciar aplicação
sudo systemctl restart facial-api
```

---

### **6. Problemas de Conectividade com Laravel**

#### **Sintomas:**
- Timeout ao conectar com API Laravel
- Erro de autenticação
- Dados não sincronizam

#### **Diagnóstico:**
```bash
# Testar conectividade
curl -H "Authorization: Bearer SEU_TOKEN" \
     https://seu-site-laravel.com.br/api/employees

# Verificar configuração
su - facial-api
cd api-facial
cat .env | grep LARAVEL
```

#### **Soluções:**
```bash
# 1. Verificar token Laravel
# No seu Laravel, gerar novo token:
# $token = $user->createToken('facial-api')->plainTextToken;

# 2. Atualizar configuração
su - facial-api
cd api-facial
nano .env
# Atualizar LARAVEL_API_TOKEN

# 3. Reiniciar aplicação
sudo systemctl restart facial-api

# 4. Testar endpoint
curl http://localhost:8000/health
```

---

## 🔍 Comandos de Diagnóstico

### **Status Geral do Sistema**
```bash
# Status dos serviços
sudo systemctl status facial-api nginx

# Uso de recursos
free -h
df -h
uptime

# Processos da aplicação
ps aux | grep -E "(gunicorn|nginx|python)"

# Portas em uso
netstat -tlnp | grep -E "(80|443|8000)"
```

### **Logs Importantes**
```bash
# Logs da aplicação
tail -f /home/facial-api/api-facial/logs/api.log

# Logs do systemd
journalctl -u facial-api -f

# Logs do Nginx
tail -f /var/log/nginx/facial-api.access.log
tail -f /var/log/nginx/facial-api.error.log

# Logs do sistema
tail -f /var/log/syslog
```

### **Testes de Conectividade**
```bash
# Teste local
curl http://localhost:8000/health

# Teste externo
curl https://seu-dominio.com.br/health

# Teste de upload
curl -X POST -F "photo=@/caminho/para/foto.jpg" \
     http://localhost:8000/api/validate
```

---

## 🛠️ Comandos de Manutenção

### **Backup Completo**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/facial-api/backups"

mkdir -p $BACKUP_DIR

# Backup dos dados
tar -czf $BACKUP_DIR/facial-api-data-$DATE.tar.gz \
    /home/facial-api/api-facial/app/storage \
    /home/facial-api/api-facial/.env \
    /home/facial-api/api-facial/logs

# Backup da configuração
cp /etc/nginx/sites-available/facial-api $BACKUP_DIR/nginx-config-$DATE
cp /etc/systemd/system/facial-api.service $BACKUP_DIR/systemd-config-$DATE

echo "Backup criado em: $BACKUP_DIR/facial-api-data-$DATE.tar.gz"
```

### **Limpeza de Logs**
```bash
#!/bin/bash
# Manter apenas últimos 7 dias
find /home/facial-api/api-facial/logs -name "*.log" -mtime +7 -delete
find /var/log/nginx -name "*.log" -mtime +7 -delete

# Limpar logs do systemd (manter últimos 30 dias)
journalctl --vacuum-time=30d

echo "Limpeza de logs concluída"
```

### **Atualização da Aplicação**
```bash
#!/bin/bash
# Script para atualizar a aplicação

echo "🔄 Atualizando aplicação..."

# Parar serviço
sudo systemctl stop facial-api

# Atualizar código
su - facial-api << 'EOF'
cd api-facial
git pull
source venv/bin/activate
pip install -r requirements.txt
EOF

# Reiniciar serviço
sudo systemctl start facial-api
sudo systemctl status facial-api

echo "✅ Atualização concluída"
```

### **Monitoramento Automático**
```bash
#!/bin/bash
# Script para monitoramento (adicionar ao cron)

# Verificar se a aplicação está respondendo
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "$(date): API não está respondendo, reiniciando..." >> /var/log/facial-api-monitor.log
    systemctl restart facial-api
fi

# Verificar uso de disco
DISK_USAGE=$(df /home/facial-api | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Uso de disco alto: ${DISK_USAGE}%" >> /var/log/facial-api-monitor.log
    # Limpar logs antigos
    find /home/facial-api/api-facial/logs -name "*.log" -mtime +3 -delete
fi
```

**Para adicionar ao cron:**
```bash
sudo crontab -e
# Adicionar linha:
*/5 * * * * /home/facial-api/monitor.sh
```

---

## 📊 Otimização de Performance

### **Configuração do Gunicorn para KingHost**
```python
# gunicorn.conf.py - Otimizado para VPS 4GB
workers = 3  # Para 4GB RAM
worker_class = "sync"
max_requests = 500
max_requests_jitter = 50
timeout = 45
keepalive = 2
preload_app = True
```

### **Configuração do Nginx para Performance**
```nginx
# Adicionar ao bloco server
gzip on;
gzip_types application/json application/javascript text/css;

# Cache para arquivos estáticos
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=30r/m;
limit_req zone=api burst=10 nodelay;
```

---

## 🆘 Contatos de Emergência

### **Suporte KingHost**
- **Telefone**: 0800 721 8000
- **Chat**: Portal do cliente
- **Email**: suporte@kinghost.com.br

### **Comandos de Emergência**
```bash
# Parar tudo em caso de problema crítico
sudo systemctl stop facial-api nginx

# Verificar processos que consomem recursos
sudo kill -9 $(ps aux | grep '[g]unicorn' | awk '{print $2}')

# Reiniciar servidor (último recurso)
sudo reboot
```

---

## 📝 Checklist de Manutenção Semanal

- [ ] Verificar logs de erro
- [ ] Verificar uso de disco e memória
- [ ] Testar endpoints principais
- [ ] Verificar certificado SSL
- [ ] Fazer backup dos dados
- [ ] Limpar logs antigos
- [ ] Verificar atualizações do sistema
- [ ] Monitorar performance da API

---

*Mantenha este guia sempre atualizado e acessível para sua equipe!*