#!/usr/bin/env python3
"""
🧠 API de Reconhecimento Facial para Ponto Eletrônico
Recebe duas imagens em base64 e retorna resultado da comparação facial
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.face_matcher import compare_two_images

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/api.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

# Criar aplicação Flask
app = Flask(__name__)

# Configuração CORS
CORS(app, origins="*")

# Configurações da aplicação
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'sua-chave-secreta-super-forte-aqui'),
    DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
    MAX_CONTENT_LENGTH=20 * 1024 * 1024,  # 20MB max (duas imagens)
    FACE_TOLERANCE=float(os.getenv('FACE_TOLERANCE', '0.6'))
)

@app.route('/', methods=['GET'])
def root():
    """
    Endpoint raiz com informações da API
    """
    return jsonify({
        "message": "🧠 API de Reconhecimento Facial para Ponto Eletrônico",
        "version": "2.0.0",
        "status": "online",
        "endpoints": {
            "compare": "/api/compare",
            "health": "/health"
        },
        "features": {
            "direct_comparison": True,
            "max_file_size_mb": app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024),
            "face_tolerance": app.config['FACE_TOLERANCE']
        },
        "documentation": "https://github.com/seu-usuario/facial-api"
    })

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint de verificação de saúde da API
    """
    try:
        # Verificar se o diretório de logs existe
        logs_ok = os.path.exists('logs')
        
        return jsonify({
            "status": "healthy" if logs_ok else "degraded",
            "api": "API Reconhecimento Facial",
            "version": "1.0.0",
            "components": {
                "logs": "✅" if logs_ok else "❌"
            },
            "configuration": {
                "debug": app.config['DEBUG'],
                "face_tolerance": app.config['FACE_TOLERANCE'],
                "max_file_size_mb": app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)
            }
        })
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/compare', methods=['POST'])
def compare():
    """
    Endpoint para comparação facial entre duas imagens
    
    Request JSON:
    {
        "reference_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
        "captured_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
        "employee_id": "123" (opcional, apenas para log)
    }
    
    Response JSON:
    {
        "success": true,
        "match": true,
        "confidence": 0.92,
        "distance": 0.08,
        "threshold": 0.6
    }
    """
    try:
        # Validar se é uma requisição JSON
        if not request.is_json:
            return jsonify({
                "success": False,
                "error": "Content-Type deve ser application/json"
            }), 400
        
        data = request.get_json()
        
        # Validar campos obrigatórios
        if not data:
            return jsonify({
                "success": False,
                "error": "JSON inválido ou vazio"
            }), 400
        
        reference_image = data.get('reference_image')
        captured_image = data.get('captured_image')
        employee_id = data.get('employee_id', 'unknown')  # Opcional
        
        if not reference_image:
            return jsonify({
                "success": False,
                "error": "Campo 'reference_image' é obrigatório"
            }), 400
        
        if not captured_image:
            return jsonify({
                "success": False,
                "error": "Campo 'captured_image' é obrigatório"
            }), 400
        
        # Validar formato base64 das imagens
        for field, image in [('reference_image', reference_image), ('captured_image', captured_image)]:
            if not image.startswith('data:image/'):
                return jsonify({
                    "success": False,
                    "error": f"Campo '{field}' tem formato inválido. Use data:image/jpeg;base64,..."
                }), 400
        
        # Log da requisição
        logger.info(f"📨 Comparação facial solicitada para funcionário: {employee_id}")
        
        # Realizar comparação facial
        result = compare_two_images(
            reference_image, 
            captured_image,
            app.config['FACE_TOLERANCE']
        )
        
        # Log do resultado
        if result.get('success'):
            match_status = "✅ MATCH" if result.get('match') else "❌ NO MATCH"
            confidence = result.get('confidence', 0)
            distance = result.get('distance', 0)
            logger.info(f"🎯 Resultado para {employee_id}: {match_status} (confiança: {confidence:.3f}, distância: {distance:.4f})")
        else:
            logger.warning(f"⚠️ Erro na comparação para {employee_id}: {result.get('reason', 'Erro desconhecido')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"💥 Erro interno na comparação: {e}")
        return jsonify({
            "success": False,
            "error": "Erro interno do servidor",
            "details": str(e) if app.config['DEBUG'] else None
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para rotas não encontradas"""
    return jsonify({
        "error": "Endpoint não encontrado",
        "available_endpoints": ["/", "/health", "/api/compare"]
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handler para métodos não permitidos"""
    return jsonify({
        "error": "Método não permitido",
        "allowed_methods": ["GET", "POST"]
    }), 405

@app.errorhandler(413)
def payload_too_large(error):
    """Handler para payload muito grande"""
    return jsonify({
        "error": "Arquivo muito grande",
        "max_size": "10MB"
    }), 413

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos"""
    logger.error(f"Erro interno: {error}")
    return jsonify({
        "error": "Erro interno do servidor"
    }), 500

# Middleware para logging de requisições
@app.before_request
def log_request():
    """Log das requisições recebidas"""
    logger.info(f"📥 {request.method} {request.path} - IP: {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log das respostas enviadas"""
    logger.info(f"📤 {request.method} {request.path} - Status: {response.status_code}")
    return response

if __name__ == '__main__':
    logger.info("🚀 Iniciando API de Reconhecimento Facial")
    logger.info(f"🎯 Endpoint principal: /api/compare")
    logger.info(f"⚙️ Face tolerance: {app.config['FACE_TOLERANCE']}")
    logger.info(f"📦 Max file size: {app.config['MAX_CONTENT_LENGTH'] // (1024 * 1024)}MB")
    logger.info(f"🔧 Debug mode: {app.config['DEBUG']}")
    
    # Executar aplicação
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )