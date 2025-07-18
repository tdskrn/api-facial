# Serviço de reconhecimento facial SIMULADO (para testes sem dependências pesadas)
import os
from typing import Optional, Tuple
import aiofiles
from loguru import logger
import json
from datetime import datetime

from app.config import settings

class FacialService:
    """
    Serviço SIMULADO para reconhecimento facial (para testes)
    
    ATENÇÃO: Esta é uma versão de demonstração que simula o reconhecimento facial.
    Para produção real, use Docker com todas as dependências instaladas.
    """
    
    def __init__(self):
        self.tolerance = settings.FACE_TOLERANCE
        self.storage_path = settings.STORAGE_PATH
        self.temp_path = settings.TEMP_PATH
        
        logger.info("🎭 Serviço Facial MOCK iniciado - versão de demonstração")
        
    async def save_employee_photo(self, employee_id: str, image_bytes: bytes) -> Tuple[bool, str]:
        """
        SIMULA salvamento de foto (salva arquivo sem processar)
        """
        try:
            logger.info(f"📷 [MOCK] Simulando salvamento para funcionário {employee_id}")
            
            # Simular validação básica
            if len(image_bytes) < 1000:  # Muito pequeno
                return False, "Arquivo muito pequeno. Envie uma imagem real."
            
            if len(image_bytes) > settings.MAX_FILE_SIZE:
                return False, f"Arquivo muito grande. Máximo: {settings.MAX_FILE_SIZE // (1024*1024)}MB"
            
            # Salvar arquivo original
            photo_path = os.path.join(self.storage_path, f"{employee_id}.jpg")
            async with aiofiles.open(photo_path, 'wb') as f:
                await f.write(image_bytes)
            
            # Simular encoding (dados fictícios para demonstração)
            encoding_data = {
                "employee_id": employee_id,
                "encoding": [0.1, 0.2, 0.3] * 50,  # Encoding simulado
                "face_location": [50, 100, 150, 200],
                "created_at": datetime.now().isoformat(),
                "tolerance": self.tolerance,
                "version": "1.0-MOCK",
                "note": "Este é um encoding simulado para demonstração"
            }
            
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            async with aiofiles.open(encoding_path, 'w') as f:
                await f.write(json.dumps(encoding_data, indent=2))
            
            logger.info(f"✅ [MOCK] Funcionário {employee_id} 'registrado' com sucesso")
            return True, f"[MOCK] Foto do funcionário {employee_id} registrada (simulação)"
                
        except Exception as e:
            logger.error(f"❌ [MOCK] Erro ao salvar funcionário {employee_id}: {e}")
            return False, f"Erro simulado: {str(e)}"
    
    async def verify_face(self, employee_id: str, image_bytes: bytes) -> Tuple[bool, float, str]:
        """
        SIMULA verificação facial (sempre retorna 85% de similaridade)
        """
        try:
            logger.info(f"🔍 [MOCK] Simulando verificação para funcionário {employee_id}")
            
            # Verificar se existe 'encoding' salvo
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            
            if not os.path.exists(encoding_path):
                logger.warning(f"⚠️ [MOCK] Funcionário {employee_id} não registrado")
                return False, 0.0, "not_registered"
            
            # Simular validação da imagem
            if len(image_bytes) < 1000:
                return False, 0.0, "invalid_image"
            
            # SIMULAÇÃO: Sempre reconhece com 85% de similaridade
            is_match = True
            similarity = 0.85  # 85%
            confidence = "high"
            
            logger.info(f"🎯 [MOCK] Funcionário {employee_id} 'reconhecido' com {similarity:.1%}")
            
            return is_match, similarity, confidence
            
        except Exception as e:
            logger.error(f"❌ [MOCK] Erro na verificação do funcionário {employee_id}: {e}")
            return False, 0.0, "error"
    
    def employee_has_photo(self, employee_id: str) -> bool:
        """Verifica se funcionário tem arquivos salvos"""
        photo_path = os.path.join(self.storage_path, f"{employee_id}.jpg")
        encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
        
        has_both = os.path.exists(photo_path) and os.path.exists(encoding_path)
        
        if has_both:
            logger.debug(f"✅ [MOCK] Funcionário {employee_id} possui arquivos")
        else:
            logger.debug(f"❌ [MOCK] Funcionário {employee_id} não possui arquivos")
            
        return has_both
    
    async def delete_employee_data(self, employee_id: str) -> bool:
        """Remove arquivos do funcionário"""
        try:
            photo_path = os.path.join(self.storage_path, f"{employee_id}.jpg")
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            
            removed_files = []
            
            if os.path.exists(photo_path):
                os.remove(photo_path)
                removed_files.append("foto")
            
            if os.path.exists(encoding_path):
                os.remove(encoding_path)
                removed_files.append("encoding")
            
            if removed_files:
                logger.info(f"🗑️ [MOCK] Arquivos removidos para funcionário {employee_id}: {', '.join(removed_files)}")
                return True
            else:
                logger.info(f"ℹ️ [MOCK] Nenhum arquivo encontrado para funcionário {employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ [MOCK] Erro ao remover dados do funcionário {employee_id}: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Retorna estatísticas do sistema"""
        try:
            files = os.listdir(self.storage_path) if os.path.exists(self.storage_path) else []
            
            photos = len([f for f in files if f.endswith('.jpg')])
            encodings = len([f for f in files if f.endswith('_encoding.json')])
            
            complete_employees = 0
            for file in files:
                if file.endswith('.jpg'):
                    employee_id = file.replace('.jpg', '')
                    if self.employee_has_photo(employee_id):
                        complete_employees += 1
            
            return {
                "mode": "MOCK/DEMO",
                "note": "Esta é uma versão de demonstração sem reconhecimento facial real",
                "total_photos": photos,
                "total_encodings": encodings,
                "complete_employees": complete_employees,
                "storage_path": self.storage_path,
                "tolerance": self.tolerance,
                "real_facial_recognition": False
            }
            
        except Exception as e:
            logger.error(f"❌ [MOCK] Erro ao obter estatísticas: {e}")
            return {
                "error": str(e),
                "mode": "MOCK/DEMO"
            }

# Instância global do serviço facial MOCK
facial_service = FacialService() 