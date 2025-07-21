#!/usr/bin/env python3
"""
🧪 Script de Teste para Integração com Laravel
Testa a API Flask que busca fotos via API Laravel
"""

import requests
import json
import base64
import sys
import os
from io import BytesIO
from PIL import Image, ImageDraw

# Configurações
API_URL = "http://localhost:8000"
EMPLOYEE_ID = "123"

def create_test_image():
    """Cria uma imagem de teste simples"""
    # Criar uma imagem de teste 200x200 com um "rosto" simples
    img = Image.new('RGB', (200, 200), color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # Desenhar um rosto simples
    # Cabeça (círculo)
    draw.ellipse([50, 50, 150, 150], fill='peachpuff', outline='black', width=2)
    
    # Olhos
    draw.ellipse([70, 80, 90, 100], fill='black')
    draw.ellipse([110, 80, 130, 100], fill='black')
    
    # Nariz
    draw.polygon([(100, 100), (95, 110), (105, 110)], fill='pink')
    
    # Boca
    draw.arc([80, 115, 120, 135], start=0, end=180, fill='red', width=3)
    
    # Converter para base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

def test_health():
    """Testa o endpoint de health check"""
    print("🔍 Testando health check...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check OK")
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   API: {data.get('api')}")
            
            # Verificar configuração Laravel
            config = data.get('configuration', {})
            laravel_api = config.get('laravel_api', 'N/A')
            authenticated = config.get('authenticated', False)
            
            print(f"   Laravel API: {laravel_api}")
            print(f"   Autenticado: {'✅' if authenticated else '❌'}")
            
            if not authenticated:
                print("   ⚠️ ATENÇÃO: Token Laravel não configurado!")
                
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro no health check: {e}")
        return False
    
    return True

def test_root():
    """Testa o endpoint raiz"""
    print("🏠 Testando endpoint raiz...")
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            print("✅ Endpoint raiz OK")
            data = response.json()
            print(f"   Mensagem: {data.get('message')}")
            
            # Verificar integração Laravel
            laravel_info = data.get('laravel_integration', {})
            print(f"   Laravel API Base: {laravel_info.get('api_base')}")
            print(f"   Token Configurado: {'✅' if laravel_info.get('authenticated') else '❌'}")
            
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")

def test_validate_with_laravel():
    """Testa o endpoint de validação que busca foto via Laravel"""
    print("📷 Testando validação com integração Laravel...")
    
    # Criar imagem de teste
    test_image_b64 = create_test_image()
    
    payload = {
        "employee_id": EMPLOYEE_ID,
        "image_base64": test_image_b64
    }
    
    try:
        print(f"   Enviando requisição para funcionário ID: {EMPLOYEE_ID}")
        
        response = requests.post(
            f"{API_URL}/api/validate",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                print("✅ Validação processada com sucesso")
                if 'match' in data:
                    match_status = "MATCH" if data['match'] else "NO MATCH"
                    confidence = data.get('confidence', 0)
                    print(f"   Resultado: {match_status} (confiança: {confidence:.2f})")
            else:
                reason = data.get('reason', 'Razão não especificada')
                print(f"⚠️ Validação falhou: {reason}")
                
                # Detectar problemas específicos
                if "não foi possível obter" in reason.lower():
                    print("   💡 Possíveis causas:")
                    print("      - Funcionário não existe na API Laravel")
                    print("      - Token de autenticação inválido")
                    print("      - API Laravel não está respondendo")
                    print("      - URL da API Laravel incorreta")
                elif "não foi possível processar" in reason.lower():
                    print("   💡 Problema na imagem capturada")
                
        elif response.status_code == 500:
            print("❌ Erro interno do servidor")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error', 'Erro desconhecido')}")
                details = error_data.get('details')
                if details:
                    print(f"   Detalhes: {details}")
            except:
                print(f"   Resposta: {response.text}")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error', 'Erro desconhecido')}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na validação: {e}")

def test_laravel_api_directly():
    """Testa se conseguimos acessar a API Laravel diretamente"""
    print("🔍 Testando acesso direto à API Laravel...")
    
    # Tentar descobrir as configurações
    try:
        response = requests.get(f"{API_URL}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            laravel_info = data.get('laravel_integration', {})
            laravel_base = laravel_info.get('api_base')
            authenticated = laravel_info.get('authenticated')
            
            if not laravel_base:
                print("❌ Laravel API Base não configurado")
                return
                
            print(f"   Laravel API: {laravel_base}")
            print(f"   Token: {'Configurado' if authenticated else 'Não configurado'}")
            
            # Testar endpoint Laravel
            laravel_url = f"{laravel_base}/api/employee/{EMPLOYEE_ID}/photo"
            print(f"   Testando: {laravel_url}")
            
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            # Nota: não podemos testar com token real aqui pois não temos acesso
            # Mas podemos testar se o endpoint responde
            
            try:
                laravel_response = requests.get(laravel_url, headers=headers, timeout=10)
                print(f"   Status Laravel: {laravel_response.status_code}")
                
                if laravel_response.status_code == 401:
                    print("   ✅ API Laravel respondeu (mas precisa de autenticação)")
                elif laravel_response.status_code == 404:
                    print("   ⚠️ Funcionário não encontrado ou endpoint não existe")
                elif laravel_response.status_code == 200:
                    print("   ✅ API Laravel funcionando!")
                    try:
                        laravel_data = laravel_response.json()
                        print(f"   Dados: {json.dumps(laravel_data, indent=2)}")
                    except:
                        pass
                else:
                    print(f"   ❓ Status inesperado: {laravel_response.status_code}")
                    
            except requests.exceptions.ConnectionError:
                print("   ❌ Não foi possível conectar à API Laravel")
                print("   💡 Verifique se a URL está correta e o servidor está funcionando")
            except requests.exceptions.Timeout:
                print("   ❌ Timeout ao conectar à API Laravel")
            except Exception as e:
                print(f"   ❌ Erro ao testar API Laravel: {e}")
        
    except Exception as e:
        print(f"❌ Erro ao obter configurações: {e}")

def show_configuration_help():
    """Mostra ajuda sobre configuração"""
    print("\n📋 CONFIGURAÇÃO NECESSÁRIA")
    print("=" * 50)
    print()
    print("Para usar esta API, você precisa configurar:")
    print()
    print("1. No arquivo .env da API Flask:")
    print("   LARAVEL_API_BASE=https://meusite-laravel.com.br")
    print("   LARAVEL_API_TOKEN=1|abc123...")
    print()
    print("2. No seu Laravel, crie o endpoint:")
    print("   GET /api/employee/{id}/photo")
    print("   (veja laravel-api-example.php)")
    print()
    print("3. No Laravel, gere um token Sanctum:")
    print("   $token = $user->createToken('facial-api')->plainTextToken;")
    print()
    print("4. O endpoint Laravel deve retornar:")
    print("   {")
    print('     "success": true,')
    print('     "employee_id": "123",')
    print('     "photo_url": "https://site.com/storage/employees/123.jpg"')
    print("   }")

def main():
    print("🧪 Teste de Integração Flask + Laravel")
    print("=" * 50)
    
    # Verificar se a API está rodando
    if not test_health():
        print("\n❌ API Flask não está respondendo. Certifique-se de que está rodando:")
        print("   python3 app.py")
        print("   ou")
        print("   gunicorn --config gunicorn.conf.py app:app")
        sys.exit(1)
    
    print("\n📋 Executando testes...")
    
    # Executar todos os testes
    test_root()
    print()
    
    test_laravel_api_directly()
    print()
    
    test_validate_with_laravel()
    print()
    
    show_configuration_help()
    print()
    
    print("✅ Testes concluídos!")

if __name__ == "__main__":
    main()