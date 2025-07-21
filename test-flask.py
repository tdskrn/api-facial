#!/usr/bin/env python3
"""
🧪 Script de Teste para API Flask de Reconhecimento Facial
Testa a nova API baseada em Flask
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
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")

def test_validate_with_mock_image():
    """Testa o endpoint de validação com imagem mock"""
    print("📷 Testando validação com imagem mock...")
    
    # Criar imagem de teste
    test_image_b64 = create_test_image()
    
    payload = {
        "employee_id": EMPLOYEE_ID,
        "image_base64": test_image_b64
    }
    
    try:
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
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error', 'Erro desconhecido')}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na validação: {e}")

def test_validate_errors():
    """Testa cenários de erro no endpoint de validação"""
    print("🚨 Testando cenários de erro...")
    
    # Teste 1: JSON vazio
    print("   Teste 1: JSON vazio")
    try:
        response = requests.post(f"{API_URL}/api/validate", json={})
        print(f"   Status: {response.status_code} (esperado: 400)")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 2: employee_id faltando
    print("   Teste 2: employee_id faltando")
    try:
        response = requests.post(f"{API_URL}/api/validate", json={"image_base64": "test"})
        print(f"   Status: {response.status_code} (esperado: 400)")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 3: image_base64 faltando
    print("   Teste 3: image_base64 faltando")
    try:
        response = requests.post(f"{API_URL}/api/validate", json={"employee_id": "123"})
        print(f"   Status: {response.status_code} (esperado: 400)")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 4: formato base64 inválido
    print("   Teste 4: formato base64 inválido")
    try:
        response = requests.post(f"{API_URL}/api/validate", json={
            "employee_id": "123",
            "image_base64": "formato_invalido"
        })
        print(f"   Status: {response.status_code} (esperado: 400)")
    except Exception as e:
        print(f"   Erro: {e}")

def test_404():
    """Testa endpoint inexistente"""
    print("🔍 Testando endpoint inexistente...")
    try:
        response = requests.get(f"{API_URL}/endpoint-inexistente")
        print(f"   Status: {response.status_code} (esperado: 404)")
    except Exception as e:
        print(f"   Erro: {e}")

def main():
    print("🧪 Iniciando testes da API Flask de Reconhecimento Facial")
    print("=" * 60)
    
    # Verificar se a API está rodando
    if not test_health():
        print("\n❌ API não está respondendo. Certifique-se de que está rodando:")
        print("   python3 app.py")
        print("   ou")
        print("   gunicorn --config gunicorn.conf.py app:app")
        sys.exit(1)
    
    print("\n📋 Executando testes...")
    
    # Executar todos os testes
    test_root()
    print()
    
    test_validate_with_mock_image()
    print()
    
    test_validate_errors()
    print()
    
    test_404()
    print()
    
    print("✅ Testes concluídos!")
    print("\n📚 Para testar com imagem real:")
    print("   1. Coloque uma foto em test.jpg")
    print("   2. Execute: python3 test-real-image.py")

if __name__ == "__main__":
    main()