# Endpoints da API de reconhecimento facial
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional
import aiofiles
from loguru import logger
from datetime import datetime

# Importar serviço facial com fallback inteligente
try:
    from app.services.facial_service import facial_service
    SERVICE_MODE = "real" if facial_service.facial_recognition_available else "limited"
    logger.info(f"✅ Serviço facial carregado em modo: {SERVICE_MODE}")
except ImportError as e:
    # Fallback para versão mock se houver erro crítico
    logger.warning(f"⚠️ Erro ao carregar serviço facial: {e}")
    try:
        from app.services.facial_service_mock import facial_service
        SERVICE_MODE = "mock"
        logger.info("🎭 Usando serviço facial MOCK como fallback")
    except ImportError as e2:
        logger.error(f"❌ Erro crítico: não foi possível carregar nenhum serviço facial: {e2}")
        raise RuntimeError("Nenhum serviço facial disponível")
from app.config import settings
from app.models.employee import FacialVerificationResult, FacialRegistrationResult

# Criar router para endpoints de reconhecimento facial
router = APIRouter()

def validate_file(file: UploadFile) -> None:
    """
    Valida o arquivo enviado
    
    Args:
        file: Arquivo enviado via upload
        
    Raises:
        HTTPException: Se o arquivo não atender aos critérios
    """
    # Verificar se o arquivo existe
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Nenhum arquivo foi enviado"
        )
    
    # Verificar tamanho do arquivo
    if hasattr(file, 'size') and file.size and file.size > settings.MAX_FILE_SIZE:
        size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. Tamanho máximo permitido: {size_mb}MB"
        )
    
    # Verificar extensão do arquivo
    if file.filename:
        extension = file.filename.split('.')[-1].lower()
        if extension not in settings.ALLOWED_EXTENSIONS:
            allowed = ', '.join(settings.ALLOWED_EXTENSIONS)
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de arquivo não permitido. Formatos aceitos: {allowed}"
            )

@router.post(
    "/register-employee/{employee_id}",
    response_model=FacialRegistrationResult,
    summary="Registrar foto de funcionário",
    description="Registra a foto de um funcionário para uso no reconhecimento facial"
)
async def register_employee_photo(
    employee_id: str,
    file: UploadFile = File(
        ..., 
        description="Arquivo de imagem contendo o rosto do funcionário (JPG, PNG, WEBP)"
    )
):
    """
    Registra a foto de um funcionário para reconhecimento facial
    
    **Parâmetros:**
    - **employee_id**: ID único do funcionário (string)
    - **file**: Arquivo de imagem com o rosto do funcionário
    
    **Requisitos da imagem:**
    - Formato: JPG, PNG ou WEBP
    - Tamanho máximo: 10MB
    - Deve conter exatamente um rosto
    - Rosto deve ser claro e bem iluminado
    - Rosto deve ocupar boa parte da imagem
    
    **Retorna:**
    - Resultado do registro com status de sucesso/falha
    - Mensagem explicativa
    - Caminhos dos arquivos salvos (se sucesso)
    """
    try:
        logger.info(f"🎯 Recebida solicitação de registro para funcionário {employee_id}")
        
        # Validar arquivo enviado
        validate_file(file)
        
        # Verificar se funcionário já possui foto
        if facial_service.employee_has_photo(employee_id):
            logger.warning(f"⚠️ Funcionário {employee_id} já possui foto registrada")
            raise HTTPException(
                status_code=409,
                detail=f"Funcionário {employee_id} já possui foto registrada. Use o endpoint de atualização."
            )
        
        # Ler conteúdo do arquivo
        image_bytes = await file.read()
        logger.info(f"📁 Arquivo lido: {len(image_bytes)} bytes")
        
        # Salvar foto e gerar encoding
        success, message = await facial_service.save_employee_photo(employee_id, image_bytes)
        
        if success:
            photo_path = f"{settings.STORAGE_PATH}/{employee_id}.jpg"
            encoding_path = f"{settings.STORAGE_PATH}/{employee_id}_encoding.json"
            
            result = FacialRegistrationResult(
                employee_id=employee_id,
                success=True,
                message=message,
                photo_path=photo_path,
                encoding_path=encoding_path
            )
            
            logger.info(f"✅ Funcionário {employee_id} registrado com sucesso")
            return result
        else:
            logger.error(f"❌ Falha no registro do funcionário {employee_id}: {message}")
            raise HTTPException(
                status_code=400,
                detail=message
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro crítico no registro de funcionário {employee_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno do servidor. Tente novamente."
        )

@router.post(
    "/verify-face/{employee_id}",
    response_model=FacialVerificationResult,
    summary="Verificar identidade facial",
    description="Verifica se o rosto na imagem pertence ao funcionário especificado"
)
async def verify_employee_face(
    employee_id: str,
    file: UploadFile = File(
        ..., 
        description="Arquivo de imagem para verificação facial"
    )
):
    """
    Verifica se o rosto na imagem pertence ao funcionário especificado
    
    **Parâmetros:**
    - **employee_id**: ID do funcionário para verificar
    - **file**: Arquivo de imagem contendo o rosto para verificação
    
    **Processo de verificação:**
    1. Valida o arquivo enviado
    2. Verifica se o funcionário possui foto cadastrada
    3. Detecta rosto na imagem enviada
    4. Compara com o rosto cadastrado
    5. Retorna resultado com nível de confiança
    
    **Retorna:**
    - **verified**: True se o rosto pertence ao funcionário
    - **similarity**: Porcentagem de similaridade (0-100%)
    - **confidence**: Nível de confiança (high/medium/low)
    - **timestamp**: Momento da verificação
    """
    try:
        logger.info(f"🔍 Recebida solicitação de verificação para funcionário {employee_id}")
        
        # Validar arquivo enviado
        validate_file(file)
        
        # Verificar se funcionário possui foto cadastrada
        if not facial_service.employee_has_photo(employee_id):
            logger.warning(f"⚠️ Funcionário {employee_id} não possui foto cadastrada")
            raise HTTPException(
                status_code=404,
                detail=f"Funcionário {employee_id} não possui foto cadastrada. Registre uma foto primeiro."
            )
        
        # Ler conteúdo do arquivo
        image_bytes = await file.read()
        logger.info(f"📁 Arquivo de verificação lido: {len(image_bytes)} bytes")
        
        # Verificar rosto
        is_match, similarity, confidence = await facial_service.verify_face(employee_id, image_bytes)
        
        # Criar resultado da verificação
        result = FacialVerificationResult(
            employee_id=employee_id,
            verified=is_match,
            similarity=round(similarity * 100, 2),  # Converter para porcentagem
            confidence=confidence,
            timestamp=datetime.now()
        )
        
        # Log do resultado
        status_emoji = "✅" if is_match else "❌"
        logger.info(
            f"{status_emoji} Verificação concluída para funcionário {employee_id}: "
            f"Verificado={is_match}, Similaridade={result.similarity}%, Confiança={confidence}"
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro crítico na verificação do funcionário {employee_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail="Erro interno do servidor. Tente novamente."
        )

@router.put(
    "/update-employee/{employee_id}",
    response_model=FacialRegistrationResult,
    summary="Atualizar foto de funcionário",
    description="Atualiza a foto de um funcionário já cadastrado"
)
async def update_employee_photo(
    employee_id: str,
    file: UploadFile = File(
        ..., 
        description="Nova foto do funcionário"
    )
):
    """
    Atualiza a foto de um funcionário já cadastrado
    
    **Nota:** Remove a foto anterior e registra a nova
    """
    try:
        logger.info(f"🔄 Recebida solicitação de atualização para funcionário {employee_id}")
        
        # Validar arquivo
        validate_file(file)
        
        # Verificar se funcionário existe
        if not facial_service.employee_has_photo(employee_id):
            raise HTTPException(
                status_code=404,
                detail=f"Funcionário {employee_id} não encontrado. Use o endpoint de registro."
            )
        
        # Remover dados antigos
        await facial_service.delete_employee_data(employee_id)
        logger.info(f"🗑️ Dados antigos removidos para funcionário {employee_id}")
        
        # Ler e processar nova foto
        image_bytes = await file.read()
        success, message = await facial_service.save_employee_photo(employee_id, image_bytes)
        
        if success:
            result = FacialRegistrationResult(
                employee_id=employee_id,
                success=True,
                message=f"Foto do funcionário {employee_id} atualizada com sucesso",
                photo_path=f"{settings.STORAGE_PATH}/{employee_id}.jpg",
                encoding_path=f"{settings.STORAGE_PATH}/{employee_id}_encoding.json"
            )
            
            logger.info(f"✅ Funcionário {employee_id} atualizado com sucesso")
            return result
        else:
            raise HTTPException(status_code=400, detail=message)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro na atualização do funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/employee/{employee_id}/status",
    summary="Status do funcionário",
    description="Verifica se o funcionário possui foto cadastrada"
)
async def get_employee_status(employee_id: str):
    """
    Verifica o status de cadastro de um funcionário
    
    **Retorna:**
    - **employee_id**: ID do funcionário
    - **has_photo**: Se possui foto cadastrada
    - **status**: Status do cadastro (registered/not_registered)
    """
    try:
        has_photo = facial_service.employee_has_photo(employee_id)
        
        return {
            "employee_id": employee_id,
            "has_photo": has_photo,
            "status": "registered" if has_photo else "not_registered",
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro ao verificar status do funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.delete(
    "/employee/{employee_id}",
    summary="Remover dados do funcionário",
    description="Remove todos os dados faciais de um funcionário"
)
async def delete_employee_data(employee_id: str):
    """
    Remove todos os dados faciais de um funcionário
    
    **Atenção:** Esta ação é irreversível!
    """
    try:
        success = await facial_service.delete_employee_data(employee_id)
        
        if success:
            return {
                "message": f"Dados do funcionário {employee_id} removidos com sucesso",
                "employee_id": employee_id,
                "deleted_at": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum dado encontrado para o funcionário {employee_id}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erro ao remover dados do funcionário {employee_id}: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/statistics",
    summary="Estatísticas do sistema",
    description="Retorna estatísticas gerais do sistema de reconhecimento facial"
)
async def get_system_statistics():
    """
    Retorna estatísticas do sistema de reconhecimento facial
    
    **Inclui:**
    - Total de fotos armazenadas
    - Total de encodings gerados
    - Funcionários com dados completos
    - Configurações do sistema
    """
    try:
        stats = facial_service.get_statistics()
        stats["generated_at"] = datetime.now().isoformat()
        return stats
        
    except Exception as e:
        logger.error(f"❌ Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/service-info",
    summary="Informações do serviço",
    description="Retorna informações detalhadas sobre o modo de operação do serviço facial"
)
async def get_service_info():
    """
    Retorna informações sobre o modo de operação do serviço facial
    """
    try:
        return {
            "service_mode": SERVICE_MODE,
            "facial_recognition_available": getattr(facial_service, 'facial_recognition_available', False),
            "capabilities": {
                "real_face_detection": SERVICE_MODE == "real" and getattr(facial_service, 'facial_recognition_available', False),
                "face_encoding": SERVICE_MODE == "real" and getattr(facial_service, 'facial_recognition_available', False),
                "similarity_calculation": SERVICE_MODE == "real" and getattr(facial_service, 'facial_recognition_available', False),
                "image_storage": True,
                "basic_validation": True
            },
            "recommendations": {
                "install_dependencies": SERVICE_MODE != "real",
                "command": "pip install face-recognition opencv-python-headless numpy" if SERVICE_MODE != "real" else None
            },
            "checked_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erro ao obter informações do serviço: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@router.get(
    "/health",
    summary="Verificação de saúde",
    description="Endpoint para verificar se o serviço de reconhecimento facial está funcionando"
)
async def health_check():
    """
    Endpoint de verificação de saúde do serviço facial
    
    **Testa:**
    - Disponibilidade do serviço
    - Acesso aos diretórios de armazenamento
    - Configurações básicas
    """
    try:
        # Verificar se os diretórios existem
        import os
        storage_ok = os.path.exists(settings.STORAGE_PATH)
        temp_ok = os.path.exists(settings.TEMP_PATH)
        
        # Status geral baseado no modo do serviço
        if SERVICE_MODE == "real" and getattr(facial_service, 'facial_recognition_available', False):
            service_status = "fully_operational"
            service_emoji = "🎯"
        elif SERVICE_MODE == "limited":
            service_status = "limited_functionality"
            service_emoji = "⚠️"
        else:
            service_status = "simulation_mode"
            service_emoji = "🎭"
        
        return {
            "status": "healthy",
            "service": "facial_recognition",
            "service_mode": SERVICE_MODE,
            "service_status": service_status,
            "service_emoji": service_emoji,
            "version": settings.APP_VERSION,
            "tolerance": settings.FACE_TOLERANCE,
            "storage_available": storage_ok,
            "temp_available": temp_ok,
            "max_file_size_mb": settings.MAX_FILE_SIZE // (1024 * 1024),
            "allowed_extensions": list(settings.ALLOWED_EXTENSIONS),
            "facial_recognition_available": getattr(facial_service, 'facial_recognition_available', False),
            "checked_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no health check: {e}")
        raise HTTPException(status_code=500, detail="Serviço indisponível") 