# Configurações da aplicação
import os
from pydantic_settings import BaseSettings
from typing import Set

class Settings(BaseSettings):
    """
    Configurações da aplicação usando Pydantic Settings
    Carrega automaticamente do arquivo .env ou variáveis de ambiente
    """
    
    # API
    APP_NAME: str = "API Reconhecimento Facial"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Servidor
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Banco de dados
    DATABASE_URL: str = "sqlite:///./facial_api.db"
    
    # Redis (cache)
    REDIS_URL: str = "redis://localhost:6379"
    
    # Reconhecimento facial
    FACE_TOLERANCE: float = 0.6  # Ajuste conforme necessário (0.6 é padrão)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: Set[str] = {"jpg", "jpeg", "png", "webp"}
    
    # Paths de armazenamento
    STORAGE_PATH: str = "app/storage/employee_photos"
    TEMP_PATH: str = "app/storage/temp"
    
    # Segurança
    SECRET_KEY: str = "sua-chave-secreta-super-forte-aqui-mude-isso"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instância global das configurações
settings = Settings()

# Criar diretórios necessários se não existirem
def create_directories():
    """Cria os diretórios necessários para a aplicação"""
    directories = [
        settings.STORAGE_PATH,
        settings.TEMP_PATH,
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"📁 Diretório criado/verificado: {directory}")

# Executar criação de diretórios ao importar
create_directories() 