#!/usr/bin/env python3
"""
🧪 Script de Teste para Comparação Direta de Imagens
Testa a nova API que recebe duas imagens base64
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

def create_test_image(color='lightblue', face_color='peachpuff'):
    """Cria uma imagem de teste simples com um rosto"""
    # Criar uma imagem de teste 200x200
    img = Image.new('RGB', (200, 200), color=color)
    draw = ImageDraw.Draw(img)
    
    # Desenhar um rosto simples
    # Cabeça (círculo)
    draw.ellipse([50, 50, 150, 150], fill=face_color, outline='black', width=2)
    
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
            
            # Verificar configuração
            config = data.get('configuration', {})
            tolerance = config.get('face_tolerance', 'N/A')
            max_size = config.get('max_file_size_mb', 'N/A')
            
            print(f"   Face tolerance: {tolerance}")
            print(f"   Max file size: {max_size}MB")
                
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
            print(f"   Versão: {data.get('version')}")
            
            # Verificar endpoints
            endpoints = data.get('endpoints', {})
            print(f"   Endpoint principal: {endpoints.get('compare')}")
            
            # Verificar features
            features = data.get('features', {})
            print(f"   Comparação direta: {features.get('direct_comparison')}")
            print(f"   Tolerance: {features.get('face_tolerance')}")
            
        else:
            print(f"❌ Endpoint raiz falhou: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no endpoint raiz: {e}")

def test_same_images():
    """Testa comparação com a mesma imagem (deve dar match)"""
    print("📷 Testando com imagens idênticas (deve dar MATCH)...")
    
    # Criar uma imagem
    test_image = create_test_image()
    
    payload = {
        "reference_image": test_image,
        "captured_image": test_image,
        "employee_id": "test-identical"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/compare",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {json.dumps(data, indent=2)}")
            
            if data.get('success') and data.get('match'):
                confidence = data.get('confidence', 0)
                distance = data.get('distance', 0)
                print(f"✅ SUCESSO: Match detectado (confiança: {confidence:.3f}, distância: {distance:.4f})")
            else:
                print(f"❌ FALHA: Imagens idênticas não deram match!")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Erro: {error_data.get('error')}")
            except:
                print(f"   Resposta: {response.text}")
                
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

def test_different_images():
    """Testa comparação com imagens diferentes (deve dar no match)"""
    print("📷 Testando com imagens diferentes (deve dar NO MATCH)...")
    
    # Criar duas imagens diferentes
    image1 = create_test_image(color='lightblue', face_color='peachpuff')
    image2 = create_test_image(color='lightgreen', face_color='lightcoral')
    
    payload = {
        "reference_image": image1,
        "captured_image": image2,
        "employee_id": "test-different"
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/compare",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Resposta: {json.dumps(data, indent=2)}")
            
            if data.get('success'):
                match = data.get('match')
                confidence = data.get('confidence', 0)
                distance = data.get('distance', 0)
                
                if not match:
                    print(f"✅ SUCESSO: No match detectado corretamente (confiança: {confidence:.3f}, distância: {distance:.4f})")
                else:
                    print(f"⚠️ ATENÇÃO: Imagens diferentes deram match (pode ser normal para rostos similares)")
            else:
                reason = data.get('reason', 'Razão não especificada')
                print(f"⚠️ Comparação falhou: {reason}")
                
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
                
    except Exception as e:
        print(f"❌ Erro na comparação: {e}")

def test_error_scenarios():
    """Testa cenários de erro"""
    print("🚨 Testando cenários de erro...")
    
    # Teste 1: JSON vazio
    print("   Teste 1: JSON vazio")
    try:
        response = requests.post(f"{API_URL}/api/compare", json={})
        print(f"   Status: {response.status_code} (esperado: 400)")
        if response.status_code == 400:
            print("   ✅ Erro detectado corretamente")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 2: Campo faltando
    print("   Teste 2: Campo reference_image faltando")
    try:
        response = requests.post(f"{API_URL}/api/compare", json={
            "captured_image": "data:image/jpeg;base64,test"
        })
        print(f"   Status: {response.status_code} (esperado: 400)")
        if response.status_code == 400:
            print("   ✅ Erro detectado corretamente")
    except Exception as e:
        print(f"   Erro: {e}")
    
    # Teste 3: Formato base64 inválido
    print("   Teste 3: Formato base64 inválido")
    try:
        response = requests.post(f"{API_URL}/api/compare", json={
            "reference_image": "formato_invalido",
            "captured_image": "formato_invalido"
        })
        print(f"   Status: {response.status_code} (esperado: 400)")
        if response.status_code == 400:
            print("   ✅ Erro detectado corretamente")
    except Exception as e:
        print(f"   Erro: {e}")

def test_with_real_images():
    """Testa com imagens reais se disponíveis"""
    print("📸 Verificando imagens reais...")
    
    test_files = ['test1.jpg', 'test2.jpg', 'reference.jpg', 'captured.jpg']
    available_files = [f for f in test_files if os.path.exists(f)]
    
    if len(available_files) >= 2:
        print(f"   Encontradas {len(available_files)} imagens de teste")
        
        # Carregar duas primeiras imagens
        with open(available_files[0], 'rb') as f:
            img1_data = base64.b64encode(f.read()).decode()
            img1_b64 = f"data:image/jpeg;base64,{img1_data}"
        
        with open(available_files[1], 'rb') as f:
            img2_data = base64.b64encode(f.read()).decode()
            img2_b64 = f"data:image/jpeg;base64,{img2_data}"
        
        payload = {
            "reference_image": img1_b64,
            "captured_image": img2_b64,
            "employee_id": "test-real-images"
        }
        
        try:
            response = requests.post(
                f"{API_URL}/api/compare",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    match = "MATCH" if data.get('match') else "NO MATCH"
                    confidence = data.get('confidence', 0)
                    print(f"   Resultado: {match} (confiança: {confidence:.3f})")
                else:
                    print(f"   Erro: {data.get('reason')}")
            else:
                print(f"   Erro HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   Erro: {e}")
    else:
        print("   Nenhuma imagem real encontrada")
        print("   💡 Para testar com imagens reais:")
        print("      1. Coloque arquivos JPG nesta pasta")
        print("      2. Nomeie como: test1.jpg, test2.jpg, etc.")

def main():
    print("🧪 Teste de Comparação Direta de Imagens")
    print("=" * 50)
    
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
    
    test_same_images()
    print()
    
    test_different_images()
    print()
    
    test_error_scenarios()
    print()
    
    test_with_real_images()
    print()
    
    print("✅ Testes concluídos!")
    print("\n📚 Como usar a API:")
    print("POST /api/compare")
    print('''{
  "reference_image": "data:image/jpeg;base64,...",
  "captured_image": "data:image/jpeg;base64,...",
  "employee_id": "123"
}''')
    print("\nResposta:")
    print('''{
  "success": true,
  "match": true,
  "confidence": 0.923,
  "distance": 0.077,
  "threshold": 0.6
}''')

if __name__ == "__main__":
    main()