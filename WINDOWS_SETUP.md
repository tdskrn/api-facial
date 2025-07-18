# 🪟 Setup no Windows - API de Reconhecimento Facial

Guia específico para executar a API de Reconhecimento Facial no Windows.

## 🛠️ Pré-requisitos Windows

### **1. Instalar Docker Desktop**

1. Baixar Docker Desktop: https://www.docker.com/products/docker-desktop
2. Instalar e reiniciar o computador
3. Abrir Docker Desktop e aguardar inicialização

### **2. Configurar WSL2 (Recomendado)**

```powershell
# Abrir PowerShell como Administrador
wsl --install

# Reiniciar computador
# Configurar usuário Linux
```

### **3. Instalar Git (se não tiver)**

1. Baixar: https://git-scm.com/downloads
2. Instalar com configurações padrão

## 🚀 Deploy no Windows

### **Opção 1: Via PowerShell (Diretamente)**

```powershell
# 1. Clonar o repositório
git clone https://github.com/seu-usuario/api-facial.git
cd api-facial

# 2. Criar arquivo .env manualmente
copy env.example .env
# Editar .env no Notepad se necessário

# 3. Iniciar apenas a API (desenvolvimento)
docker-compose up --build -d facial-api

# 4. Verificar se funcionou
docker-compose ps
```

### **Opção 2: Via WSL2 (Recomendado para Produção)**

```bash
# 1. Abrir WSL2 (Ubuntu)
wsl

# 2. Navegar para a pasta do projeto
cd /mnt/c/caminho/para/api-facial

# 3. Dar permissões aos scripts
chmod +x deploy.sh
chmod +x test_api.sh

# 4. Executar deploy
./deploy.sh development
```

## 🌐 Testando a API

### **Verificar se está funcionando:**

```powershell
# Teste simples
curl http://localhost:8000/health

# Ou abrir no navegador:
start http://localhost:8000/docs
```

### **Teste completo:**

```powershell
# No PowerShell
.\test_api.sh

# Ou no WSL2
./test_api.sh
```

## 📋 Comandos Windows Específicos

### **PowerShell equivalentes:**

```powershell
# Ver logs
docker-compose logs -f facial-api

# Status dos containers
docker-compose ps

# Parar aplicação
docker-compose down

# Reiniciar
docker-compose restart facial-api

# Rebuild completo
docker-compose up --build -d
```

### **Testar endpoints manualmente:**

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:8000/health"

# Status de funcionário
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/employee/123/status"

# Registrar funcionário (com foto)
$form = @{
    file = Get-Item "C:\caminho\para\foto.jpg"
}
Invoke-WebRequest -Uri "http://localhost:8000/api/v1/register-employee/123" -Method Post -Form $form
```

## 🔧 Troubleshooting Windows

### **Docker Desktop não inicia:**

1. Verificar se Hyper-V está habilitado
2. Verificar se WSL2 está instalado
3. Reiniciar Docker Desktop

### **Erro de porta ocupada:**

```powershell
# Verificar quem está usando a porta 8000
netstat -ano | findstr :8000

# Matar processo se necessário
taskkill /PID <PID_NUMBER> /F
```

### **Erro de permissão de arquivo:**

```powershell
# No PowerShell como Administrador
icacls "E:\api-facial" /grant Everyone:F /T
```

### **WSL2 não funciona:**

1. Verificar se está habilitado:
   ```powershell
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```

2. Baixar kernel WSL2: https://wslstorestorage.blob.core.windows.net/wslblob/wsl_update_x64.msi

## 🖥️ Desenvolvimento no Windows

### **Editor recomendado: VS Code**

```powershell
# Instalar extensões úteis
code --install-extension ms-vscode-remote.remote-wsl
code --install-extension ms-python.python
code --install-extension ms-vscode.vscode-docker
```

### **Abrindo projeto no VS Code:**

```powershell
# Direto no Windows
code .

# Ou via WSL2 (recomendado)
wsl
cd /mnt/c/seu/projeto
code .
```

## 📁 Estrutura de Pastas Windows

```
E:\api-facial\
├── app\
│   ├── storage\
│   │   ├── employee_photos\    # Fotos dos funcionários
│   │   └── temp\              # Arquivos temporários
├── logs\                      # Logs da aplicação
├── data\                      # Banco de dados SQLite
├── deploy.sh                  # Script de deploy (Linux)
├── test_api.sh               # Script de teste (Linux)
├── docker-compose.yml
├── Dockerfile
└── README.md
```

## 🎯 Comandos Rápidos

### **Setup inicial completo:**

```powershell
# 1. Clone
git clone https://github.com/seu-usuario/api-facial.git
cd api-facial

# 2. Crie .env
copy env.example .env

# 3. Inicie
docker-compose up --build -d facial-api

# 4. Teste
start http://localhost:8000/docs
```

### **Deploy de produção:**

```powershell
# Para produção com Nginx
docker-compose up --build -d facial-api nginx

# Teste
start http://localhost
```

## 🔍 URLs Importantes

- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Estatísticas**: http://localhost:8000/api/v1/statistics
- **Nginx** (se ativo): http://localhost

## 💡 Dicas Windows

1. **Use WSL2** para melhor compatibilidade com Docker
2. **Docker Desktop** deve estar sempre rodando
3. **Antivírus** pode interferir - adicione pasta do projeto às exceções
4. **Windows Defender** pode bloquear Docker - configure exceções
5. **PowerShell como Admin** para alguns comandos
6. **VS Code + WSL** oferece melhor experiência de desenvolvimento

## 🆘 Suporte Windows

Se tiver problemas:

1. Verificar logs: `docker-compose logs facial-api`
2. Reiniciar Docker Desktop
3. Verificar se WSL2 está funcionando: `wsl --list --verbose`
4. Testar conexão: `curl http://localhost:8000/health`

---

**✅ Com este setup, sua API estará rodando perfeitamente no Windows!** 🚀 