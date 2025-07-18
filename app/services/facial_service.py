# Serviço de reconhecimento facial
import face_recognition
import cv2
import numpy as np
import os
from typing import Optional, Tuple
import aiofiles
from loguru import logger
import hashlib
import json
from datetime import datetime

from app.config import settings

class FacialService:
    """
    Serviço principal para reconhecimento facial
    
    Responsável por:
    - Salvar fotos de funcionários
    - Gerar encodings faciais
    - Verificar identidade facial
    - Gerenciar armazenamento de dados faciais
    """
    
    def __init__(self):
        self.tolerance = settings.FACE_TOLERANCE
        self.storage_path = settings.STORAGE_PATH
        self.temp_path = settings.TEMP_PATH
        
        # Configurar logger específico para o serviço facial
        logger.add(
            "logs/facial_service.log",
            rotation="1 day",
            retention="30 days",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | FACIAL | {level} | {message}"
        )
        
    async def save_employee_photo(self, employee_id: str, image_bytes: bytes) -> Tuple[bool, str]:
        """
        Salva a foto do funcionário e gera encoding facial
        
        Args:
            employee_id: ID único do funcionário
            image_bytes: Bytes da imagem
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            logger.info(f"📷 Iniciando salvamento de foto para funcionário {employee_id}")
            
            # Validar se a imagem contém um rosto válido
            is_valid, validation_message = await self._validate_face_image(image_bytes)
            if not is_valid:
                logger.warning(f"⚠️ Imagem inválida para funcionário {employee_id}: {validation_message}")
                return False, validation_message
            
            # Caminhos para salvar a foto e encoding
            photo_path = os.path.join(self.storage_path, f"{employee_id}.jpg")
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            
            # Salvar a imagem original
            async with aiofiles.open(photo_path, 'wb') as f:
                await f.write(image_bytes)
            
            # Gerar e salvar o encoding facial
            success, encoding_message = await self._generate_and_save_encoding(employee_id, image_bytes)
            
            if success:
                logger.info(f"✅ Foto e encoding salvos com sucesso para funcionário {employee_id}")
                return True, f"Foto do funcionário {employee_id} registrada com sucesso"
            else:
                # Remover foto se não conseguiu gerar encoding
                if os.path.exists(photo_path):
                    os.remove(photo_path)
                    logger.info(f"🗑️ Foto removida devido a falha no encoding: {employee_id}")
                return False, encoding_message
                
        except Exception as e:
            logger.error(f"❌ Erro crítico ao salvar foto do funcionário {employee_id}: {e}")
            return False, f"Erro interno ao processar imagem: {str(e)}"
    
    async def _validate_face_image(self, image_bytes: bytes) -> Tuple[bool, str]:
        """
        Valida se a imagem contém exatamente um rosto detectável
        
        Args:
            image_bytes: Bytes da imagem
            
        Returns:
            Tuple[bool, str]: (é_válida, mensagem)
        """
        try:
            # Converter bytes para imagem numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                return False, "Não foi possível decodificar a imagem"
            
            # Converter para RGB (necessário para face_recognition)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detectar rostos na imagem
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                return False, "Nenhum rosto foi detectado na imagem. Certifique-se de que há um rosto claro e bem iluminado."
            
            if len(face_locations) > 1:
                return False, f"Múltiplos rostos detectados ({len(face_locations)}). A imagem deve conter apenas um rosto."
            
            # Verificar qualidade do rosto detectado
            top, right, bottom, left = face_locations[0]
            face_width = right - left
            face_height = bottom - top
            
            # Verificar se o rosto não é muito pequeno
            if face_width < 50 or face_height < 50:
                return False, "O rosto detectado é muito pequeno. Use uma imagem com rosto maior e mais próximo."
            
            return True, "Imagem válida com um rosto detectado"
            
        except Exception as e:
            logger.error(f"❌ Erro na validação da imagem: {e}")
            return False, f"Erro ao validar imagem: {str(e)}"
    
    async def _generate_and_save_encoding(self, employee_id: str, image_bytes: bytes) -> Tuple[bool, str]:
        """
        Gera encoding facial e salva como arquivo JSON
        
        Args:
            employee_id: ID do funcionário
            image_bytes: Bytes da imagem
            
        Returns:
            Tuple[bool, str]: (sucesso, mensagem)
        """
        try:
            # Converter bytes para imagem numpy
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Encontrar localizações dos rostos
            face_locations = face_recognition.face_locations(rgb_image)
            
            # Gerar encodings faciais
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if not face_encodings:
                return False, "Não foi possível gerar encoding facial. Tente uma imagem com melhor qualidade."
            
            # Preparar dados do encoding para salvar
            encoding_data = {
                "employee_id": employee_id,
                "encoding": face_encodings[0].tolist(),  # Converter numpy array para lista
                "face_location": face_locations[0],      # Localização do rosto na imagem
                "created_at": datetime.now().isoformat(),
                "tolerance": self.tolerance,
                "version": "1.0"  # Versão do formato para compatibilidade futura
            }
            
            # Salvar encoding como arquivo JSON
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            async with aiofiles.open(encoding_path, 'w') as f:
                await f.write(json.dumps(encoding_data, indent=2))
            
            logger.info(f"💾 Encoding facial salvo: {encoding_path}")
            return True, "Encoding facial gerado com sucesso"
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar encoding para funcionário {employee_id}: {e}")
            return False, f"Erro ao gerar encoding facial: {str(e)}"
    
    async def verify_face(self, employee_id: str, image_bytes: bytes) -> Tuple[bool, float, str]:
        """
        Verifica se o rosto na imagem pertence ao funcionário especificado
        
        Args:
            employee_id: ID do funcionário para verificar
            image_bytes: Bytes da imagem para verificação
            
        Returns:
            Tuple[bool, float, str]: (é_mesmo_funcionário, similaridade, confiança)
        """
        try:
            logger.info(f"🔍 Iniciando verificação facial para funcionário {employee_id}")
            
            # Verificar se existe encoding salvo para o funcionário
            encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
            
            if not os.path.exists(encoding_path):
                logger.warning(f"⚠️ Encoding não encontrado para funcionário {employee_id}")
                return False, 0.0, "not_registered"
            
            # Carregar encoding conhecido do funcionário
            async with aiofiles.open(encoding_path, 'r') as f:
                content = await f.read()
                encoding_data = json.loads(content)
                known_encoding = np.array(encoding_data["encoding"])
            
            # Processar imagem de verificação
            nparr = np.frombuffer(image_bytes, np.uint8)
            unknown_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if unknown_image is None:
                return False, 0.0, "invalid_image"
            
            rgb_image = cv2.cvtColor(unknown_image, cv2.COLOR_BGR2RGB)
            
            # Encontrar rostos na imagem de verificação
            face_locations = face_recognition.face_locations(rgb_image)
            
            if not face_locations:
                logger.info(f"ℹ️ Nenhum rosto encontrado na verificação para funcionário {employee_id}")
                return False, 0.0, "no_face"
            
            # Gerar encodings dos rostos encontrados
            unknown_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if not unknown_encodings:
                logger.info(f"ℹ️ Não foi possível gerar encoding da imagem de verificação para funcionário {employee_id}")
                return False, 0.0, "encoding_failed"
            
            # Calcular distância entre os encodings (menor distância = maior similaridade)
            distances = face_recognition.face_distance([known_encoding], unknown_encodings[0])
            distance = distances[0]
            
            # Converter distância em porcentagem de similaridade
            similarity = max(0, 1 - distance)  # Garantir que não seja negativo
            
            # Determinar se é uma correspondência baseado na tolerância
            is_match = distance <= self.tolerance
            
            # Determinar nível de confiança
            if similarity >= 0.85:
                confidence = "high"
            elif similarity >= 0.70:
                confidence = "medium"
            else:
                confidence = "low"
            
            logger.info(
                f"🎯 Verificação facial funcionário {employee_id}: "
                f"Match={is_match}, Similaridade={similarity:.2%}, "
                f"Distância={distance:.3f}, Confiança={confidence}"
            )
            
            return is_match, similarity, confidence
            
        except Exception as e:
            logger.error(f"❌ Erro crítico na verificação facial do funcionário {employee_id}: {e}")
            return False, 0.0, "error"
    
    def employee_has_photo(self, employee_id: str) -> bool:
        """
        Verifica se o funcionário possui foto e encoding cadastrados
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            bool: True se possui foto e encoding
        """
        photo_path = os.path.join(self.storage_path, f"{employee_id}.jpg")
        encoding_path = os.path.join(self.storage_path, f"{employee_id}_encoding.json")
        
        has_both = os.path.exists(photo_path) and os.path.exists(encoding_path)
        
        if has_both:
            logger.debug(f"✅ Funcionário {employee_id} possui foto e encoding")
        else:
            logger.debug(f"❌ Funcionário {employee_id} não possui foto/encoding completos")
            
        return has_both
    
    async def delete_employee_data(self, employee_id: str) -> bool:
        """
        Remove todos os dados faciais de um funcionário
        
        Args:
            employee_id: ID do funcionário
            
        Returns:
            bool: True se removido com sucesso
        """
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
                logger.info(f"🗑️ Dados removidos para funcionário {employee_id}: {', '.join(removed_files)}")
                return True
            else:
                logger.info(f"ℹ️ Nenhum dado encontrado para remover do funcionário {employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao remover dados do funcionário {employee_id}: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """
        Retorna estatísticas do sistema de reconhecimento facial
        
        Returns:
            dict: Estatísticas do sistema
        """
        try:
            # Contar arquivos no diretório de storage
            files = os.listdir(self.storage_path) if os.path.exists(self.storage_path) else []
            
            photos = len([f for f in files if f.endswith('.jpg')])
            encodings = len([f for f in files if f.endswith('_encoding.json')])
            
            # Funcionários com dados completos
            complete_employees = 0
            for file in files:
                if file.endswith('.jpg'):
                    employee_id = file.replace('.jpg', '')
                    if self.employee_has_photo(employee_id):
                        complete_employees += 1
            
            return {
                "total_photos": photos,
                "total_encodings": encodings,
                "complete_employees": complete_employees,
                "storage_path": self.storage_path,
                "tolerance": self.tolerance
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter estatísticas: {e}")
            return {
                "error": str(e)
            }

# Instância global do serviço facial
facial_service = FacialService() 