# 🎯 API de Reconhecimento Facial

Uma API completa de reconhecimento facial desenvolvida com **FastAPI** para sistemas de ponto eletrônico, otimizada para **400+ funcionários** e pronta para deploy na **Hetzner Cloud**.

## 🚀 Características

- **🔍 Reconhecimento Facial Avançado**: Utilizando `face_recognition` + `OpenCV`
- **⚡ Performance Otimizada**: Suporta 50-80 verificações simultâneas
- **🐳 Docker Ready**: Deploy com um comando
- **📊 Monitoramento**: Logs detalhados e métricas
- **🔒 Segurança**: Rate limiting, validações e headers de segurança
- **📚 Documentação Automática**: Swagger UI integrado
- **💾 Backup Automático**: Sistema de backup das fotos

## 📋 Requisitos Mínimos

### **Servidor (Hetzner Cloud)**
- **VPS**: CX31 (2 vCPU, 8GB RAM, 80GB SSD) - €7.35/mês
- **Volume**: 100GB adicional - €4.80/mês
- **Total**: ~€12/mês para 400 funcionários

### **Sistema**
- Ubuntu 20.04+ ou Debian 11+
- Docker 20.10+
- Docker Compose 2.0+

## 🛠️ Instalação Rápida

### **1. Primeira vez no servidor (instalar Docker)**

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/api-facial.git
cd api-facial

# Dar permissão ao script
chmod +x deploy.sh

# Instalar Docker (Ubuntu/Debian)
./deploy.sh install-docker

# Logout e login novamente
exit
# ssh root@seu-servidor-ip
```

### **2. Deploy da aplicação**

```bash
# Deploy completo para produção
./deploy.sh production

# OU para desenvolvimento (apenas API)
./deploy.sh development
```

### **3. Verificar se funcionou**

```bash
# Verificar status
./deploy.sh status

# Ver logs
./deploy.sh logs
```

## 🌐 Endpoints da API

### **📋 Informações**
- **Documentação**: `http://seu-ip/docs`
- **API**: `http://seu-ip:8000`
- **Health Check**: `http://seu-ip/health`

### **👤 Gestão de Funcionários**

#### **Registrar funcionário**
```bash
curl -X POST "http://seu-ip/api/v1/register-employee/123" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@foto_funcionario.jpg"
```

#### **Verificar identidade**
```bash
curl -X POST "http://seu-ip/api/v1/verify-face/123" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@foto_verificacao.jpg"
```

#### **Atualizar foto**
```bash
curl -X PUT "http://seu-ip/api/v1/update-employee/123" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@nova_foto.jpg"
```

#### **Verificar status**
```bash
curl "http://seu-ip/api/v1/employee/123/status"
```

#### **Remover funcionário**
```bash
curl -X DELETE "http://seu-ip/api/v1/employee/123"
```

### **📊 Monitoramento**

#### **Estatísticas do sistema**
```bash
curl "http://seu-ip/api/v1/statistics"
```

#### **Health check detalhado**
```bash
curl "http://seu-ip/api/v1/health"
```

## 📁 Estrutura do Projeto

```
api-facial/
├── app/
│   ├── __init__.py
│   ├── main.py                 # Aplicação principal FastAPI
│   ├── config.py               # Configurações
│   ├── api/
│   │   ├── __init__.py
│   │   └── facial.py           # Endpoints da API
│   ├── services/
│   │   ├── __init__.py
│   │   └── facial_service.py   # Lógica de reconhecimento
│   ├── models/
│   │   ├── __init__.py
│   │   └── employee.py         # Modelos de dados
│   └── storage/
│       ├── employee_photos/    # Fotos dos funcionários
│       └── temp/              # Arquivos temporários
├── logs/                      # Logs da aplicação
├── requirements.txt           # Dependências Python
├── Dockerfile                 # Configuração Docker
├── docker-compose.yml         # Orquestração de serviços
├── nginx.conf                 # Configuração Nginx
├── deploy.sh                  # Script de deploy
├── env.example                # Exemplo de configurações
└── README.md                  # Esta documentação
```

## ⚙️ Configuração

### **Arquivo .env (criado automaticamente)**

```bash
# Configurações da aplicação
DEBUG=false
SECRET_KEY=sua-chave-secreta-gerada-automaticamente

# Reconhecimento facial
FACE_TOLERANCE=0.6              # Tolerância (0.6 = padrão)
MAX_FILE_SIZE=10485760          # 10MB máximo por arquivo
ALLOWED_EXTENSIONS=jpg,jpeg,png,webp

# Banco de dados
DATABASE_URL=sqlite:///./data/facial_api.db

# Senhas (geradas automaticamente)
POSTGRES_PASSWORD=senha-segura
REDIS_PASSWORD=senha-segura
GRAFANA_PASSWORD=senha-segura
```

### **Ajustes de Performance**

Para **400 funcionários** com **picos de 80 simultâneos**:

```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      memory: 2G      # Limite de RAM
      cpus: '1.0'     # Limite de CPU
    reservations:
      memory: 512M    # RAM mínima
      cpus: '0.5'     # CPU mínima
```

## 🔧 Comandos Úteis

### **Script de Deploy**

```bash
# Ver todas as opções
./deploy.sh

# Deploy produção
./deploy.sh production

# Deploy desenvolvimento
./deploy.sh development

# Parar aplicação
./deploy.sh stop

# Ver logs em tempo real
./deploy.sh logs

# Status dos containers
./deploy.sh status

# Backup das fotos
./deploy.sh backup
```

### **Docker Compose Direto**

```bash
# Iniciar apenas a API
docker-compose up -d facial-api

# Iniciar produção completa
docker-compose up -d

# Ver logs
docker-compose logs -f facial-api

# Parar tudo
docker-compose down

# Reconstruir e iniciar
docker-compose up --build -d
```

## 📊 Monitoramento e Logs

### **Logs da Aplicação**

```bash
# Logs em tempo real
tail -f logs/api.log

# Logs de erro
tail -f logs/errors.log

# Logs do serviço facial
tail -f logs/facial_service.log
```

### **Logs do Docker**

```bash
# Logs de todos os serviços
docker-compose logs

# Logs apenas da API
docker-compose logs facial-api

# Logs apenas do Nginx
docker-compose logs nginx
```

## 🛡️ Segurança

### **Rate Limiting**
- **API geral**: 30 requisições/minuto
- **Upload de fotos**: 10 uploads/minuto
- **Burst**: Até 10 requisições extras

### **Validações**
- **Formatos aceitos**: JPG, PNG, WEBP
- **Tamanho máximo**: 10MB
- **Detecção**: Apenas 1 rosto por imagem
- **Qualidade**: Rosto mínimo 50x50 pixels

### **Headers de Segurança**
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
```

## 🚨 Troubleshooting

### **API não responde**

```bash
# Verificar containers
docker-compose ps

# Ver logs de erro
docker-compose logs facial-api

# Reiniciar API
docker-compose restart facial-api
```

### **Erro de reconhecimento facial**

```bash
# Verificar logs do serviço
tail -f logs/facial_service.log

# Verificar se diretórios existem
ls -la app/storage/employee_photos/

# Testar com curl
curl -f http://localhost:8000/health
```

### **Performance lenta**

```bash
# Verificar uso de recursos
docker stats

# Verificar logs de performance
grep "Tempo:" logs/api.log
```

## 🔄 Backup e Restauração

### **Backup Automático**

```bash
# Backup manual
./deploy.sh backup

# Backups são salvos como:
# backup_photos_YYYYMMDD_HHMMSS.tar.gz
```

### **Restauração**

```bash
# Restaurar de backup
tar -xzf backup_photos_20231201_143022.tar.gz

# Copiar para local correto
cp -r app/storage/employee_photos/* app/storage/employee_photos/
```

## 📈 Escalabilidade

### **Para mais de 400 funcionários:**

1. **Upgrade do servidor**: CX41 (4 vCPU, 16GB RAM)
2. **PostgreSQL**: Migrar de SQLite para PostgreSQL
3. **Redis**: Ativar cache Redis
4. **Load Balancer**: Usar Hetzner Load Balancer
5. **Multiple Workers**: Aumentar workers no Dockerfile

```dockerfile
# Para 1000+ funcionários
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "8"]
```

## 💡 Integração com Sistema Laravel

### **Exemplo de chamada PHP:**

```php
// Verificar funcionário
$client = new \GuzzleHttp\Client();
$response = $client->post('http://api-facial:8000/api/v1/verify-face/123', [
    'multipart' => [
        [
            'name' => 'file',
            'contents' => fopen($photoPath, 'r'),
            'filename' => 'photo.jpg'
        ]
    ]
]);

$result = json_decode($response->getBody(), true);
if ($result['verified']) {
    // Funcionário verificado com sucesso
    $similarity = $result['similarity']; // 95.67%
    $confidence = $result['confidence']; // "high"
}
```

## 🆘 Suporte

### **Problemas Comuns**

1. **"face_recognition not found"**: Reinstalar dependências
2. **"Permission denied"**: Verificar permissões dos diretórios
3. **"Out of memory"**: Aumentar RAM do servidor
4. **"No face detected"**: Melhorar qualidade da foto

### **Contato**

- **Issues**: [GitHub Issues](https://github.com/seu-usuario/api-facial/issues)
- **Email**: suporte@empresa.com
- **Documentação**: `http://seu-ip/docs`

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🎉 Pronto para Produção!

Com este setup, você tem uma **API de reconhecimento facial completa** e **otimizada para 400+ funcionários**, pronta para integrar com seu sistema de ponto eletrônico Laravel!

**Custo total na Hetzner**: ~€12/mês (~R$ 65/mês) 🚀 