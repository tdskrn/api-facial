# Dockerfile para API de Reconhecimento Facial
# Base: Python 3.11 slim (menor tamanho, segura)
FROM python:3.11-slim as base

# Metadados da imagem
LABEL maintainer="facial-api@empresa.com"
LABEL description="API de Reconhecimento Facial para Sistema de Ponto Eletrônico"
LABEL version="1.0.0"

# Configurar variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema necessárias para reconhecimento facial
RUN apt-get update && apt-get install -y \
    # OpenCV dependencies
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    # face_recognition dependencies
    cmake \
    build-essential \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    # Utilitários
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Criar usuário não-root para segurança
RUN groupadd -g 1000 appuser && \
    useradd -r -u 1000 -g appuser appuser

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários com permissões corretas
RUN mkdir -p \
    app/storage/employee_photos \
    app/storage/temp \
    logs \
    && chown -R appuser:appuser /app

# Mudar para usuário não-root
USER appuser

# Expor porta da aplicação
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão para iniciar a aplicação
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]

##############################################################################
# Dockerfile Multi-stage para desenvolvimento
##############################################################################

FROM base as development

# Instalar dependências de desenvolvimento
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy

# Sobrescrever comando para modo desenvolvimento
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

##############################################################################
# Dockerfile Multi-stage para produção
##############################################################################

FROM base as production

# Otimizações para produção
ENV DEBUG=false

# Usar múltiplos workers para produção
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"] 