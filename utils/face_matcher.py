#!/usr/bin/env python3
"""
🧠 Módulo de Comparação Facial
Compara faces usando URLs de referência e imagens base64
"""

import face_recognition
import numpy as np
import requests
import base64
import logging
from io import BytesIO
from PIL import Image
import urllib.parse

# Configuração de logging
logger = logging.getLogger(__name__)

# Configurações
THRESHOLD = 0.6  # Limiar para considerar match
REQUEST_TIMEOUT = 10  # Timeout para download de imagens (segundos)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB

def get_reference_image_from_laravel_api(employee_id, laravel_api_base, api_token=None):
    """
    Busca a imagem de referência via API Laravel
    
    Args:
        employee_id (str): ID do funcionário
        laravel_api_base (str): URL base da API Laravel
        api_token (str): Token de autenticação (opcional)
        
    Returns:
        numpy.ndarray: Imagem carregada ou None em caso de erro
    """
    try:
        # Construir URL da API Laravel
        api_url = f"{laravel_api_base}/api/employee/{employee_id}/photo"
        
        logger.info(f"📞 Buscando foto do funcionário {employee_id} via Laravel API: {api_url}")
        
        # Headers para a requisição
        headers = {
            'User-Agent': 'API-Facial-Recognition/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        # Adicionar token de autenticação se fornecido
        if api_token:
            headers['Authorization'] = f'Bearer {api_token}'
        
        # Fazer requisição para API Laravel
        response = requests.get(
            api_url,
            headers=headers,
            timeout=REQUEST_TIMEOUT
        )
        
        if response.status_code == 404:
            logger.warning(f"⚠️ Funcionário {employee_id} não encontrado na API Laravel")
            return None
        elif response.status_code == 401:
            logger.error(f"❌ Não autorizado para acessar API Laravel (token inválido?)")
            return None
        elif response.status_code != 200:
            logger.error(f"❌ Erro HTTP {response.status_code} na API Laravel: {response.text}")
            return None
        
        # Processar resposta JSON
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"❌ Resposta inválida da API Laravel: {e}")
            return None
        
        # Extrair URL da imagem da resposta
        image_url = data.get('photo_url') or data.get('image_url') or data.get('url')
        
        if not image_url:
            logger.error(f"❌ URL da imagem não encontrada na resposta da API Laravel: {data}")
            return None
        
        logger.info(f"📥 URL da imagem obtida: {image_url}")
        
        # Baixar a imagem usando a URL obtida
        return load_image_from_url(image_url)
        
    except requests.RequestException as e:
        logger.error(f"❌ Erro de rede ao acessar API Laravel: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao buscar imagem via Laravel API: {e}")
        return None

def load_image_from_url(url):
    """
    Carrega uma imagem a partir de uma URL
    
    Args:
        url (str): URL da imagem de referência
        
    Returns:
        numpy.ndarray: Imagem carregada ou None em caso de erro
    """
    try:
        logger.info(f"📥 Baixando imagem de referência: {url}")
        
        # Validar URL
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            logger.error(f"❌ URL inválida: {url}")
            return None
        
        # Fazer requisição HTTP
        headers = {
            'User-Agent': 'API-Facial-Recognition/1.0',
            'Accept': 'image/jpeg,image/png,image/webp,image/*'
        }
        
        response = requests.get(
            url, 
            timeout=REQUEST_TIMEOUT,
            headers=headers,
            stream=True
        )
        
        # Verificar status da resposta
        if response.status_code == 404:
            logger.warning(f"⚠️ Imagem de referência não encontrada: {url}")
            return None
        elif response.status_code != 200:
            logger.error(f"❌ Erro HTTP {response.status_code} ao baixar imagem: {url}")
            return None
        
        # Verificar tamanho do conteúdo
        content_length = response.headers.get('content-length')
        if content_length and int(content_length) > MAX_IMAGE_SIZE:
            logger.error(f"❌ Imagem muito grande: {content_length} bytes")
            return None
        
        # Ler conteúdo da resposta
        image_data = BytesIO()
        downloaded_size = 0
        
        for chunk in response.iter_content(chunk_size=8192):
            downloaded_size += len(chunk)
            if downloaded_size > MAX_IMAGE_SIZE:
                logger.error(f"❌ Imagem excede tamanho máximo durante download")
                return None
            image_data.write(chunk)
        
        image_data.seek(0)
        
        # Verificar se é uma imagem válida
        try:
            with Image.open(image_data) as pil_img:
                # Converter para RGB se necessário
                if pil_img.mode != 'RGB':
                    pil_img = pil_img.convert('RGB')
                
                # Verificar dimensões mínimas
                if pil_img.width < 50 or pil_img.height < 50:
                    logger.error(f"❌ Imagem muito pequena: {pil_img.width}x{pil_img.height}")
                    return None
                
                logger.info(f"✅ Imagem carregada: {pil_img.width}x{pil_img.height}")
                
                # Reset para o início do buffer
                image_data.seek(0)
                
                # Carregar com face_recognition
                img = face_recognition.load_image_file(image_data)
                return img
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar imagem: {e}")
            return None
        
    except requests.RequestException as e:
        logger.error(f"❌ Erro de rede ao baixar imagem: {e}")
        return None
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao carregar imagem: {e}")
        return None

def load_image_from_base64(b64_string):
    """
    Carrega uma imagem a partir de string base64
    
    Args:
        b64_string (str): String base64 no formato data:image/jpeg;base64,/9j/4AAQ...
        
    Returns:
        numpy.ndarray: Imagem carregada ou None em caso de erro
    """
    try:
        logger.debug("📷 Processando imagem capturada (base64)")
        
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
            logger.error(f"❌ Imagem decodificada muito grande: {len(img_data)} bytes")
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
                    logger.error(f"❌ Imagem capturada muito pequena: {pil_img.width}x{pil_img.height}")
                    return None
                
                logger.info(f"✅ Imagem capturada processada: {pil_img.width}x{pil_img.height}")
                
                # Reset para o início do buffer
                image_buffer.seek(0)
                
                # Carregar com face_recognition
                img = face_recognition.load_image_file(image_buffer)
                return img
                
        except Exception as e:
            logger.error(f"❌ Erro ao processar imagem capturada: {e}")
            return None
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado ao carregar imagem base64: {e}")
        return None

def compare_faces_with_laravel_api(employee_id, captured_b64, laravel_api_base, api_token=None):
    """
    Compara imagem capturada com imagem de referência obtida via API Laravel
    
    Args:
        employee_id (str): ID do funcionário
        captured_b64 (str): Imagem capturada em formato base64
        laravel_api_base (str): URL base da API Laravel
        api_token (str): Token de autenticação (opcional)
        
    Returns:
        dict: Resultado da comparação
        {
            "success": bool,
            "match": bool,
            "confidence": float,
            "reason": str (opcional)
        }
    """
    try:
        logger.info(f"🔍 Iniciando comparação facial para funcionário {employee_id}")
        
        # Buscar imagem de referência via API Laravel
        reference_img = get_reference_image_from_laravel_api(employee_id, laravel_api_base, api_token)
        if reference_img is None:
            return {
                "success": False,
                "reason": "Não foi possível obter a imagem de referência do funcionário"
            }
        
        # Carregar imagem capturada
        captured_img = load_image_from_base64(captured_b64)
        if captured_img is None:
            return {
                "success": False,
                "reason": "Não foi possível processar a imagem capturada"
            }
        
        # Realizar comparação facial
        return perform_face_comparison(reference_img, captured_img)
        
    except Exception as e:
        logger.error(f"❌ Erro inesperado na comparação via Laravel API: {e}")
        return {
            "success": False,
            "reason": f"Erro interno: {str(e)}"
        }

def compare_faces(reference_url, captured_b64):
    """
    Compara duas imagens faciais: uma de referência (URL) e uma capturada (base64)
    
    Args:
        reference_url (str): URL da imagem de referência
        captured_b64 (str): Imagem capturada em formato base64
        
    Returns:
        dict: Resultado da comparação
        {
            "success": bool,
            "match": bool,
            "confidence": float,
            "reason": str (opcional)
        }
    """
    try:
        logger.info(f"🔍 Iniciando comparação facial")
        logger.info(f"📍 URL de referência: {reference_url}")
        
        # Carregar imagem de referência
        reference_img = load_image_from_url(reference_url)
        if reference_img is None:
            return {
                "success": False,
                "reason": "Não foi possível carregar a imagem de referência"
            }
        
        # Carregar imagem capturada
        captured_img = load_image_from_base64(captured_b64)
        if captured_img is None:
            return {
                "success": False,
                "reason": "Não foi possível processar a imagem capturada"
            }
        
        # Realizar comparação facial
        return perform_face_comparison(reference_img, captured_img)
        
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

def perform_face_comparison(reference_img, captured_img):
    """
    Realiza a comparação facial entre duas imagens já carregadas
    
    Args:
        reference_img (numpy.ndarray): Imagem de referência
        captured_img (numpy.ndarray): Imagem capturada
        
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
        match = distance < THRESHOLD
        
        # Calcular confiança (aproximação)
        # Confiança = 1 - distância, limitada entre 0 e 1
        confidence = max(0.0, min(1.0, 1.0 - distance))
        
        # Log do resultado
        match_emoji = "✅" if match else "❌"
        logger.info(f"{match_emoji} Resultado: distância={distance:.4f}, threshold={THRESHOLD}, match={match}")
        logger.info(f"📊 Confiança: {confidence:.2f} ({confidence*100:.1f}%)")
        
        return {
            "success": True,
            "match": match,
            "confidence": round(confidence, 3),
            "distance": round(distance, 4),
            "threshold": THRESHOLD
        }
        
    except Exception as e:
        logger.error(f"❌ Erro na comparação facial: {e}")
        return {
            "success": False,
            "reason": f"Erro na comparação: {str(e)}"
        }

def set_threshold(new_threshold):
    """
    Define um novo threshold para comparação facial
    
    Args:
        new_threshold (float): Novo valor do threshold (0.0 a 1.0)
    """
    global THRESHOLD
    if 0.0 <= new_threshold <= 1.0:
        THRESHOLD = new_threshold
        logger.info(f"✅ Threshold atualizado para: {THRESHOLD}")
    else:
        logger.error(f"❌ Threshold inválido: {new_threshold}. Deve estar entre 0.0 e 1.0")

def get_threshold():
    """
    Retorna o threshold atual
    
    Returns:
        float: Valor atual do threshold
    """
    return THRESHOLD