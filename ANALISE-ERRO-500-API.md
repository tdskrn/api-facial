# 🔍 Análise do Erro 500 - API Facial

## ✅ Progresso Identificado

**Antes:** `Connection refused` (porta 8000)
**Agora:** Erro 500 `Erro interno do servidor`

🎯 **Isso significa que:**
- ✅ Laravel conseguiu conectar na API
- ✅ Nginx está funcionando e fazendo proxy
- ✅ Payload está chegando na API
- ❌ API está retornando erro interno (500)

---

## 📊 Análise do Payload

### **Dados recebidos do Flutter:**
```json
{
  "photo_current": "data:image/jpeg;base64,/9j/4QPWRXhpZgAATU0AKgAAAAgACgEAAAQAAAABAAACWAEQAAIAAAALAAAAhgEBAAQAAAABAAADIAEPAAIAAAAHAAAAkQExAAIAAAABAAAAAAEOAAIAAAABAAAAAIdpAAQAAAABAAAArAESAAMAAAABAAAAAAEyAAIAAAAUAAAAmIglAAQAAAABAAACaAAAAAAyMTA2MTExMEFHAFhpYW9taQAyMDI1OjA3OjIxIDIzOjUxOjUwAAAbkAAAAgAAAAUAAAH2kgQACgAAAAEAAAH7iCIAAwAAAAEAAAAAkgUABQAAAAEAAAIDkgMACgAAAAEAAAILkAMAAgAAABQAAAIToAAAAgAAAAUAAAInkpEAAgAAAAQyMTUApAMAAwAAAAEAAAAAoAUABAAAAAEAAANIiDIABAAAAAEAAAAApAIAAwAAAAEAAAAAgpoABQAAAAEAAAIskgkAAwAAAAEAEAAAkpAAAgAAAAQyMTUAgp0ABQAAAAEAAAI0iCcAAwAAAAEB0AAApAUAAwAAAAEAAAAAkpIAAgAAAAQyMTUApAQABQAAAAEAAAI8kAQAAgAAABQAAAJEkgEACgAAAAEAAAJYkgcAAwAAAAEAAgAAkgoABQAAAAEAAAJgiDAAAwAAAAEAAAAApAYAAwAAAAEAAAAAkggAAwAAAAEA/wAAAAAAADAyMjAAAAAAAAAAAAoAAADIAAAAZAAAAEQAAAAKMjAyNTowNzoyMSAyMzo1MTo1MAAwMTAwAAAAAaAAACcQAABftAAAJxAAD0JAAAAnEDIwMjU6MDc6MjEgMjM6NTE6NTAAAAAD6AAAA+gAAAzGAAAD6AAKAAIABQAAAAMAAALmAAYABQAAAAEAAAL+AAEAAgAAAAJTAAAAAAUAAQAAAAEAAAAAABsAAgAAAAcAAAMGAAAAAQAAAAQCAgAAAAMAA..."
}
```

### **Resposta da API:**
```json
{
  "success": false,
  "message": "Erro no microserviço de validação facial",
  "error_details": {
    "status": 500,
    "response": "{\"details\":null,\"error\":\"Erro interno do servidor\",\"success\":false}\n",
    "microservice_url": "http://arcanun-tech.vps-kinghost.net"
  }
}
```

---

## 🔍 Possíveis Causas do Erro 500

### 1. **Problema no formato do payload**
A API `/api/compare` espera:
```json
{
  "reference_image": "base64_string",
  "comparison_image": "base64_string"
}
```

Mas o Laravel está enviando:
```json
{
  "photo_current": "base64_string"
}
```

### 2. **Falta da imagem de referência**
A API precisa de duas imagens para comparar, mas só está recebendo uma.

### 3. **Problema na API interna**
Erro na aplicação FastAPI ao processar a requisição.

---

## 🧪 Testes para Diagnóstico

### **1. Testar a API diretamente**
```bash
# Testar se a API está funcionando
curl -X POST http://arcanun-tech.vps-kinghost.net/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "reference_image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
    "comparison_image": "data:image/jpeg;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
  }'
```

### **2. Verificar logs da API**
```bash
# Logs da aplicação
sudo journalctl -u facial-api -f

# Logs do Nginx
sudo tail -f /var/log/nginx/api_compare.log
sudo tail -f /var/log/nginx/api_error.log

# Logs da aplicação (se houver)
tail -f /path/to/api/logs/api.log
```

### **3. Verificar se a API está rodando**
```bash
# Verificar processo
sudo netstat -tlnp | grep :8000
ps aux | grep python
ps aux | grep uvicorn

# Testar localmente
curl -X GET http://127.0.0.1:8000/
curl -X GET http://127.0.0.1:8000/health
```

---

## 🔧 Possíveis Soluções

### **Solução 1: Corrigir o payload no Laravel**

O Laravel precisa enviar o payload correto:

```php
// Em vez de:
$payload = [
    'photo_current' => $photoBase64
];

// Usar:
$payload = [
    'reference_image' => $referencePhotoBase64,  // Foto cadastrada
    'comparison_image' => $photoBase64           // Foto atual
];
```

### **Solução 2: Verificar se a API está configurada corretamente**

1. **Verificar se a aplicação está rodando:**
   ```bash
   sudo systemctl status facial-api
   sudo systemctl restart facial-api
   ```

2. **Verificar dependências:**
   ```bash
   cd /path/to/api
   pip install -r requirements.txt
   ```

3. **Testar manualmente:**
   ```bash
   cd /path/to/api
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### **Solução 3: Verificar configuração da API**

Verificar se a rota `/api/compare` está implementada corretamente na API FastAPI.

---

## 📝 Checklist de Verificação

- [ ] API rodando na porta 8000
- [ ] Nginx fazendo proxy corretamente
- [ ] Logs da API para identificar erro específico
- [ ] Payload com formato correto (reference_image + comparison_image)
- [ ] Imagem de referência disponível no Laravel
- [ ] Dependências da API instaladas
- [ ] Rota `/api/compare` implementada

---

## 🎯 Próximos Passos

1. **Verificar logs da API** para identificar o erro específico
2. **Corrigir o payload** no Laravel para incluir ambas as imagens
3. **Testar a API diretamente** com curl
4. **Verificar se a aplicação está rodando** corretamente

---

## 💡 Observação Importante

O erro mudou de "Connection refused" para "Erro interno do servidor", o que indica que:

✅ **Nginx está funcionando**
✅ **Conexão está sendo estabelecida**
❌ **Problema agora é interno da API**

Isso é um progresso! Agora precisamos focar na correção do payload e verificação dos logs da API.