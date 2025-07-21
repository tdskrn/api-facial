#!/usr/bin/env python3
"""
🧠 API de Reconhecimento Facial para Ponto Eletrônico
Versão Flask para deploy em VPS KingHost
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.face_matcher import compare_faces_with_laravel_api

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
    LARAVEL_API_BASE=os.getenv('LARAVEL_API_BASE', 'https://meusite-laravel.com.br'),
    LARAVEL_API_TOKEN=os.getenv('LARAVEL_API_TOKEN', None),
    DEBUG=os.getenv('DEBUG', 'False').lower() == 'true',
    MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 10MB max file size
)

@app.route('/', methods=['GET'])
def root():
    """
    Endpoint raiz com informações da API
    """
    return jsonify({
        "message": "🧠 API de Reconhecimento Facial para Ponto Eletrônico",
        "version": "1.0.0",
        "status": "online",
        "endpoints": {
            "validate": "/api/validate",
            "health": "/health"
        },
        "laravel_integration": {
            "api_base": app.config['LARAVEL_API_BASE'],
            "authenticated": bool(app.config['LARAVEL_API_TOKEN'])
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
                "laravel_api": app.config['LARAVEL_API_BASE'],
                "authenticated": bool(app.config['LARAVEL_API_TOKEN'])
            }
        })
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/validate', methods=['POST'])
def validate():
    """
    Endpoint principal para validação facial
    
    Request JSON:
    {
        "employee_id": "123",
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZ..."
    }
    
    Response JSON:
    {
        "success": true,
        "match": true,
        "confidence": 0.92
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
        
        employee_id = data.get('employee_id')
        image_base64 = data.get('image_base64')
        
        if not employee_id:
            return jsonify({
                "success": False,
                "error": "Campo 'employee_id' é obrigatório"
            }), 400
        
        if not image_base64:
            return jsonify({
                "success": False,
                "error": "Campo 'image_base64' é obrigatório"
            }), 400
        
        # Validar formato base64
        if not image_base64.startswith('data:image/'):
            return jsonify({
                "success": False,
                "error": "Formato de imagem inválido. Use data:image/jpeg;base64,..."
            }), 400
        
        # Log da requisição
        logger.info(f"📨 Validação facial solicitada para funcionário: {employee_id}")
        
        # Obter configurações Laravel
        laravel_api_base = app.config['LARAVEL_API_BASE']
        laravel_api_token = app.config['LARAVEL_API_TOKEN']
        
        # Realizar comparação facial via API Laravel
        result = compare_faces_with_laravel_api(
            employee_id, 
            image_base64, 
            laravel_api_base, 
            laravel_api_token
        )
        
        # Log do resultado
        if result.get('success'):
            match_status = "✅ MATCH" if result.get('match') else "❌ NO MATCH"
            confidence = result.get('confidence', 0)
            logger.info(f"🎯 Resultado para {employee_id}: {match_status} (confiança: {confidence:.2f})")
        else:
            logger.warning(f"⚠️ Erro na validação para {employee_id}: {result.get('reason', 'Erro desconhecido')}")
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"💥 Erro interno na validação: {e}")
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
        "available_endpoints": ["/", "/health", "/api/validate"]
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
    logger.info(f"🌐 Laravel API: {app.config['LARAVEL_API_BASE']}")
    logger.info(f"🔐 Token configurado: {'Sim' if app.config['LARAVEL_API_TOKEN'] else 'Não'}")
    logger.info(f"🔧 Debug mode: {app.config['DEBUG']}")
    
    # Executar aplicação
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=app.config['DEBUG']
    )