#!/usr/bin/env python3
"""
🧠 Módulo de Comparação Facial Simplificado
Compara duas imagens base64 diretamente
"""

import face_recognition
import numpy as np
import base64
import logging
from io import BytesIO
from PIL import Image

# Configuração de logging
logger = logging.getLogger(__name__)

# Configurações
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

def load_image_from_base64(b64_string):
    """
    Carrega uma imagem a partir de string base64
    
    Args:
        b64_string (str): String base64 no formato data:image/jpeg;base64,/9j/4AAQ...
        
    Returns:
        numpy.ndarray: Imagem carregada ou None em caso de erro
    """
    try:
        logger.debug("📷 Processando imagem base64")
        
        # Validar formato
        if not b64_string.startswith('data:image/'):
            logger.error("❌ Formato base64 inválido - deve começar com 'data:image/'")
            return None
        
        # Separar header do conteúdo
        if ',' not in b64_string:
            logger.error("❌ Formato base64 inválido - separador ',' não encontrado")
            return None
        
        header, encoded = b64_string.split(",", 1)
        
        # Validar header
        valid_headers = [
            'data:image/jpeg;base64',
            'data:image/jpg;base64',
            'data:image/png;base64',
            'data:image/webp;base64'
        ]
        
        if header not in valid_headers:
            logger.error(f"❌ Formato de imagem não suportado: {header}")
            return None
        
        # Decodificar base64
        try:
            img_data = base64.b64decode(encoded)
        except Exception as e:
            logger.error(f"❌ Erro ao decodificar base64: {e}")
            return None
        
        # Verificar tamanho
        if len(img_data) > MAX_IMAGE_SIZE:
            logger.error(f"❌ Imagem muito grande: {len(img_data)} bytes")
            return None
        
        # Verificar se é uma imagem válida
        try:
            image_buffer = BytesIO(img_data)
            
            with Image.open(image_buffer) as pil_img:
                # Converter para RGB se necessário
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Verificar dimensões mínimas
                if pil_img.width < 50 or pil_img.height < 50:
                    logger.error(f"❌ Imagem muito pequena: {pil_img.width}x{pil_img.height}")
                    return None
                
                logger.debug(f"✅ Imagem processada: {pil_img.width}x{pil_img.height}")
                
                # Reset para o início do buffer
                image_buffer.seek(0)
                
                # Carregar com face_recognition
                img = face_recognition.load_image_file(image_buffer)
                return img
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar imagem: {e}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao carregar imagem base64: {e}")
        return None

def perform_face_comparison(reference_img, captured_img, threshold=0.6):
    """
    Realiza a comparação facial entre duas imagens já carregadas
    
    Args:
        reference_img (numpy.ndarray): Imagem de referência
        captured_img (numpy.ndarray): Imagem capturada
        threshold (float): Limiar para considerar match (padrão 0.6)
        
    Returns:
        dict: Resultado da comparação
    """
    try:
        # Extrair encodings faciais da imagem de referência
        logger.debug("🔍 Extraindo encoding da imagem de referência...")
        ref_encodings = face_recognition.face_encodings(reference_img)
        
        if not ref_encodings:
            logger.warning("⚠️ Nenhum rosto encontrado na imagem de referência")
            return {
                "success": False,
                "reason": "Nenhum rosto encontrado na imagem de referência"
            }
        
        if len(ref_encodings) > 1:
            logger.warning(f"⚠️ Múltiplos rostos encontrados na imagem de referência ({len(ref_encodings)}). Usando o primeiro.")
        
        # Extrair encodings faciais da imagem capturada
        logger.debug("🔍 Extraindo encoding da imagem capturada...")
        cap_encodings = face_recognition.face_encodings(captured_img)
        
        if not cap_encodings:
            logger.warning("⚠️ Nenhum rosto encontrado na imagem capturada")
            return {
                "success": False,
                "reason": "Nenhum rosto encontrado na imagem capturada"
            }
        
        if len(cap_encodings) > 1:
            logger.warning(f"⚠️ Múltiplos rostos encontrados na imagem capturada ({len(cap_encodings)}). Usando o primeiro.")
        
        # Usar o primeiro encoding de cada imagem
        ref_vector = ref_encodings[0]
        cap_vector = cap_encodings[0]
        
        # Calcular distância euclidiana
        distance = np.linalg.norm(ref_vector - cap_vector)
        
        # Determinar match baseado no threshold
        match = distance < threshold
        
        # Calcular confiança (aproximação)
        # Confiança = 1 - distância, limitada entre 0 e 1
        confidence = max(0.0, min(1.0, 1.0 - distance))
        
        # Log do resultado
        match_emoji = "✅" if match else "❌"
        logger.info(f"{match_emoji} Resultado: distância={distance:.4f}, threshold={threshold}, match={match}")
        logger.info(f"📊 Confiança: {confidence:.3f} ({confidence*100:.1f}%)")
        
        return {
            "success": True,
            "match": match,
            "confidence": round(confidence, 3),
            "distance": round(distance, 4),
            "threshold": threshold
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na comparação facial: {e}")
        return {
            "success": False,
            "reason": f"Erro na comparação: {str(e)}"
        }

def compare_two_images(reference_b64, captured_b64, threshold=0.6):
    """
    Compara duas imagens faciais em formato base64
    
    Args:
        reference_b64 (str): Imagem de referência em base64
        captured_b64 (str): Imagem capturada em base64
        threshold (float): Limiar para considerar match (padrão 0.6)
        
    Returns:
        dict: Resultado da comparação
        {
            "success": bool,
            "match": bool,
            "confidence": float,
            "distance": float,
            "threshold": float,
            "reason": str (opcional)
        }
    """
    try:
        logger.info(f"🔍 Iniciando comparação facial com threshold={threshold}")
        
        # Carregar imagem de referência
        logger.debug("📥 Carregando imagem de referência...")
        reference_img = load_image_from_base64(reference_b64)
        if reference_img is None:
            return {
                "success": False,
                "reason": "Não foi possível processar a imagem de referência"
            }
        
        # Carregar imagem capturada
        logger.debug("📥 Carregando imagem capturada...")
        captured_img = load_image_from_base64(captured_b64)
        if captured_img is None:
            return {
                "success": False,
                "reason": "Não foi possível processar a imagem capturada"
            }
        
        # Realizar comparação facial
        return perform_face_comparison(reference_img, captured_img, threshold)
        
    except ImportError as e:
        logger.error(f"❌ Dependência não encontrada: {e}")
        return {
            "success": False,
            "reason": "Bibliotecas de reconhecimento facial não estão instaladas"
        }
    except Exception as e:
        logger.error(f"❌ Erro inesperado na comparação: {e}")
        return {
            "success": False,
            "reason": f"Erro interno: {str(e)}"
        }

def set_threshold(new_threshold):
    """
    Define um novo threshold para comparação facial
    
    Args:
        new_threshold (float): Novo valor do threshold (0.0 a 1.0)
    """
    if 0.0 <= new_threshold <= 1.0:
        logger.info(f"✅ Threshold atualizado para: {new_threshold}")
        return new_threshold
    else:
        logger.error(f"❌ Threshold inválido: {new_threshold}. Deve estar entre 0.0 e 1.0")
        return 0.6  # Valor padrão

def validate_base64_image(b64_string):
    """
    Valida se a string base64 representa uma imagem válida
    
    Args:
        b64_string (str): String base64 da imagem
        
    Returns:
        dict: {"valid": bool, "reason": str (opcional)}
    """
    try:
        img = load_image_from_base64(b64_string)
        if img is not None:
            return {"valid": True}
        else:
            return {"valid": False, "reason": "Imagem inválida ou formato não suportado"}
    except Exception as e:
        return {"valid": False, "reason": str(e)}