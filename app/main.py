# Aplicação principal FastAPI
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import time
import os
import sys

from app.config import settings, create_directories
from app.api.facial import router as facial_router

# Configurar logging avançado
logger.remove()  # Remover logger padrão

# Logger para console (desenvolvimento)
if settings.DEBUG:
    logger.add(
        sys.stdout,
        level="DEBUG",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )

# Logger para arquivo (sempre ativo)
logger.add(
    "logs/api.log",
    rotation="1 day",
    retention="30 days",
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
    compression="zip"
)

# Logger para erros críticos
logger.add(
    "logs/errors.log",
    rotation="1 week",
    retention="12 weeks",
    level="ERROR",
    format="{time:YYYY-MM-DD HH:mm:ss} | ERROR | {name}:{function}:{line} | {message} | {extra}",
    backtrace=True,
    diagnose=True
)

# Criar diretórios necessários
create_directories()

# Log de inicialização
logger.info("🚀 Iniciando API de Reconhecimento Facial")
logger.info(f"📋 Configurações: DEBUG={settings.DEBUG}, TOLERANCE={settings.FACE_TOLERANCE}")

# Criar aplicação FastAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 🎯 API de Reconhecimento Facial para Sistema de Ponto Eletrônico
    
    Esta API oferece funcionalidades completas de reconhecimento facial para 
    identificação de funcionários em sistemas de ponto eletrônico.
    
    ### 🔧 Funcionalidades
    
    - **Registro de Funcionários**: Cadastro de fotos para reconhecimento
    - **Verificação Facial**: Comparação de rostos em tempo real
    - **Gestão de Dados**: CRUD completo de dados faciais
    - **Estatísticas**: Monitoramento do sistema
    - **Saúde do Sistema**: Verificação de status
    
    ### 📱 Como Usar
    
    1. **Registrar funcionário**: POST `/api/v1/register-employee/{employee_id}`
    2. **Verificar identidade**: POST `/api/v1/verify-face/{employee_id}`
    3. **Verificar status**: GET `/api/v1/employee/{employee_id}/status`
    
    ### 🔐 Requisitos de Imagem
    
    - **Formatos**: JPG, PNG, WEBP
    - **Tamanho máximo**: 10MB
    - **Conteúdo**: Exatamente um rosto claro e bem iluminado
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Middleware de CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://seudominio.com"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Middleware de host confiável (segurança)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.DEBUG else ["seudominio.com", "*.seudominio.com"]
)

# Middleware personalizado para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware para log detalhado de todas as requisições
    """
    start_time = time.time()
    
    # Informações da requisição
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log da requisição recebida
    logger.info(
        f"📨 Requisição recebida: {request.method} {request.url.path} "
        f"de {client_ip} | User-Agent: {user_agent[:50]}..."
    )
    
    try:
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de processamento
        process_time = time.time() - start_time
        
        # Determinar emoji baseado no status
        if response.status_code < 300:
            status_emoji = "✅"
        elif response.status_code < 400:
            status_emoji = "📝"
        elif response.status_code < 500:
            status_emoji = "⚠️"
        else:
            status_emoji = "❌"
        
        # Log da resposta
        logger.info(
            f"{status_emoji} Resposta enviada: {request.method} {request.url.path} | "
            f"Status: {response.status_code} | Tempo: {process_time:.4f}s"
        )
        
        # Adicionar headers de performance
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-API-Version"] = settings.APP_VERSION
        
        return response
        
    except Exception as e:
        # Log de erro crítico
        process_time = time.time() - start_time
        logger.error(
            f"💥 Erro crítico na requisição: {request.method} {request.url.path} | "
            f"Erro: {str(e)} | Tempo: {process_time:.4f}s"
        )
        
        # Retornar erro genérico
        return JSONResponse(
            status_code=500,
            content={
                "error": "Erro interno do servidor",
                "request_id": f"{int(time.time())}-{client_ip}",
                "timestamp": time.time()
            }
        )

# Handler global para exceções não tratadas
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handler global para capturar exceções não tratadas
    """
    client_ip = request.client.host if request.client else "unknown"
    
    logger.error(
        f"🚨 Exceção não tratada: {type(exc).__name__} | "
        f"Mensagem: {str(exc)} | "
        f"Endpoint: {request.method} {request.url.path} | "
        f"Cliente: {client_ip}"
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Erro interno do servidor",
            "message": "Ocorreu um erro inesperado. Tente novamente.",
            "timestamp": time.time()
        }
    )

# Incluir rotas da API
app.include_router(
    facial_router, 
    prefix="/api/v1", 
    tags=["🎯 Reconhecimento Facial"]
)

# Endpoints raiz
@app.get(
    "/",
    summary="Informações da API",
    description="Endpoint raiz com informações básicas da API"
)
async def root():
    """
    Endpoint raiz da API com informações básicas
    """
    return {
        "message": f"🎯 {settings.APP_NAME}",
        "version": settings.APP_VERSION,
        "status": "🟢 Online",
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        },
        "endpoints": {
            "health": "/health",
            "api": "/api/v1",
            "statistics": "/api/v1/statistics"
        },
        "support": {
            "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
            "allowed_formats": list(settings.ALLOWED_EXTENSIONS),
            "tolerance": settings.FACE_TOLERANCE
        }
    }

@app.get(
    "/health",
    summary="Verificação de saúde global",
    description="Endpoint para verificar se toda a API está funcionando"
)
async def health_check():
    """
    Endpoint de verificação de saúde global da API
    """
    try:
        # Verificar componentes críticos
        storage_exists = os.path.exists(settings.STORAGE_PATH)
        temp_exists = os.path.exists(settings.TEMP_PATH)
        logs_exists = os.path.exists("logs")
        
        # Calcular uptime (aproximado)
        uptime_file = "logs/startup.txt"
        if not os.path.exists(uptime_file):
            with open(uptime_file, 'w') as f:
                f.write(str(time.time()))
        
        with open(uptime_file, 'r') as f:
            start_time = float(f.read().strip())
            uptime_seconds = time.time() - start_time
        
        # Status geral
        all_healthy = storage_exists and temp_exists and logs_exists
        
        return {
            "status": "healthy" if all_healthy else "degraded",
            "api": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "uptime_seconds": round(uptime_seconds, 2),
            "uptime_human": f"{uptime_seconds // 3600:.0f}h {(uptime_seconds % 3600) // 60:.0f}m",
            "components": {
                "storage": "✅" if storage_exists else "❌",
                "temp": "✅" if temp_exists else "❌", 
                "logs": "✅" if logs_exists else "❌"
            },
            "configuration": {
                "debug": settings.DEBUG,
                "tolerance": settings.FACE_TOLERANCE,
                "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024)
            },
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check global: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            }
        )

# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Executado quando a aplicação inicia
    """
    logger.info("🎬 API inicializada com sucesso!")
    logger.info(f"🌐 Documentação disponível em: /docs")
    logger.info(f"🔍 Health check disponível em: /health")
    logger.info(f"📊 Estatísticas disponíveis em: /api/v1/statistics")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Executado quando a aplicação é encerrada
    """
    logger.info("🛑 API sendo encerrada...")
    logger.info("👋 Até logo!")

# Executar aplicação (apenas para desenvolvimento)
if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Iniciando servidor de desenvolvimento em {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="debug" if settings.DEBUG else "info"
    ) 