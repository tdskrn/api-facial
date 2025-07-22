# 🚀 Deploy Rápido na KingHost VPS

## ⚡ Instalação em 5 Minutos

### **Pré-requisitos**
- VPS KingHost com Ubuntu 20.04+ (mínimo 4GB RAM)
- Domínio apontando para o IP da VPS
- Token Bearer do seu sistema Laravel

### **Deploy Automático**
```bash
# 1. Conectar na VPS
ssh root@SEU_IP_VPS

# 2. Baixar e executar script
wget https://raw.githubusercontent.com/SEU_USUARIO/api-facial/main/deploy-kinghost-auto.sh
chmod +x deploy-kinghost-auto.sh
sudo bash deploy-kinghost-auto.sh
```

**O script irá pedir:**
- Seu domínio (ex: `api-facial.seusite.com.br`)
- URL do Laravel (ex: `https://meusite.com.br`)
- Token Bearer do Laravel

### **Configurar SSL (Após o Deploy)**
```bash
sudo certbot --nginx -d api-facial.seusite.com.br
```

---

## 📋 Deploy Manual (Passo a Passo)

Se preferir fazer manualmente, siga o guia completo:
👉 **[DEPLOY-KINGHOST.md](./DEPLOY-KINGHOST.md)**

---

## 🧪 Testar a API

```bash
# Health check
curl https://api-facial.seusite.com.br/health

# Teste de upload
curl -X POST -F "photo=@foto.jpg" \
     https://api-facial.seusite.com.br/api/validate
```

---

## 🔧 Comandos Úteis

### **Status dos Serviços**
```bash
sudo systemctl status facial-api nginx
```

### **Ver Logs**
```bash
# Logs da aplicação
sudo journalctl -u facial-api -f

# Logs do Nginx
sudo tail -f /var/log/nginx/facial-api.error.log
```

### **Reiniciar Aplicação**
```bash
sudo systemctl restart facial-api
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

---

## 🚨 Problemas Comuns

### **API não responde**
```bash
# Verificar se está rodando
sudo systemctl status facial-api

# Verificar logs
sudo journalctl -u facial-api -n 50

# Reiniciar
sudo systemctl restart facial-api
```

### **Erro 502 Bad Gateway**
```bash
# Verificar se a aplicação está na porta 8000
netstat -tlnp | grep 8000

# Testar localmente
curl http://localhost:8000/health
```

### **Upload de arquivos falha**
```bash
# Verificar permissões
sudo chown -R facial-api:facial-api /home/facial-api/api-facial/app/storage
sudo chmod -R 755 /home/facial-api/api-facial/app/storage
```

**Para mais soluções:** 👉 **[TROUBLESHOOTING-KINGHOST.md](./TROUBLESHOOTING-KINGHOST.md)**

---

## 📊 Monitoramento

### **Verificar Recursos**
```bash
# CPU e Memória
htop

# Espaço em disco
df -h

# Processos da aplicação
ps aux | grep gunicorn
```

### **Backup Automático**
```bash
# Criar backup
tar -czf backup-$(date +%Y%m%d).tar.gz \
    /home/facial-api/api-facial/app/storage \
    /home/facial-api/api-facial/.env
```

---

## 🔗 Integração com Laravel

### **1. Configurar Token no Laravel**
```php
// No seu controller Laravel
$token = $user->createToken('facial-api')->plainTextToken;
echo $token; // Use este token na configuração
```

### **2. Endpoint de Exemplo**
```php
// routes/api.php
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/employees', [EmployeeController::class, 'index']);
    Route::post('/employees/{id}/validate', [EmployeeController::class, 'validate']);
});
```

### **3. Testar Integração**
```bash
curl -H "Authorization: Bearer SEU_TOKEN" \
     https://meusite.com.br/api/employees
```

---

## 📱 URLs Importantes

- **API Health**: `https://api-facial.seusite.com.br/health`
- **Documentação**: `https://api-facial.seusite.com.br/docs`
- **Validação**: `https://api-facial.seusite.com.br/api/validate`

---

## 🆘 Suporte

### **Logs para Análise**
```bash
# Coletar logs para suporte
sudo journalctl -u facial-api -n 100 > logs-facial-api.txt
sudo tail -n 100 /var/log/nginx/facial-api.error.log > logs-nginx.txt
```

### **Informações do Sistema**
```bash
# Informações para suporte
echo "=== SISTEMA ===" > info-sistema.txt
uname -a >> info-sistema.txt
echo "\n=== PYTHON ===" >> info-sistema.txt
python3 --version >> info-sistema.txt
echo "\n=== SERVIÇOS ===" >> info-sistema.txt
sudo systemctl status facial-api nginx >> info-sistema.txt
```

### **Contato KingHost**
- **Suporte**: 0800 721 8000
- **Chat**: Portal do cliente
- **Email**: suporte@kinghost.com.br

---

## ✅ Checklist de Deploy

- [ ] VPS configurada com Ubuntu 20.04+
- [ ] Domínio apontando para o IP
- [ ] Token Laravel configurado
- [ ] Deploy executado com sucesso
- [ ] SSL configurado
- [ ] API respondendo em `/health`
- [ ] Upload de fotos funcionando
- [ ] Integração com Laravel testada
- [ ] Backup configurado
- [ ] Monitoramento ativo

---

**🎉 Sua API de Reconhecimento Facial está pronta na KingHost!**

*Para dúvidas ou problemas, consulte os guias detalhados ou entre em contato com o suporte.*