# Script de instalação para Windows
# Execute como Administrador

Write-Host "🎯 Instalando API de Reconhecimento Facial no Windows" -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green

# Verificar Python
Write-Host "`n📋 Verificando Python..." -ForegroundColor Blue
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python não encontrado. Instale Python 3.8-3.11" -ForegroundColor Red
    exit 1
}

# Atualizar pip e setuptools
Write-Host "`n🔧 Atualizando pip e setuptools..." -ForegroundColor Blue
python -m pip install --upgrade pip setuptools wheel

# Instalar Visual C++ Build Tools (necessário para dlib)
Write-Host "`n🛠️  IMPORTANTE: Se der erro, instale Visual Studio Build Tools:" -ForegroundColor Yellow
Write-Host "   https://visualstudio.microsoft.com/visual-cpp-build-tools/" -ForegroundColor Yellow

# Instalar CMake (necessário para dlib)
Write-Host "`n🔨 Instalando CMake..." -ForegroundColor Blue
python -m pip install cmake

# Tentar instalar dlib primeiro (problemático no Windows)
Write-Host "`n🎭 Instalando dlib..." -ForegroundColor Blue
python -m pip install dlib

if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Falha no dlib. Tentando alternativa..." -ForegroundColor Yellow
    # Alternativa: usar wheel pré-compilado
    python -m pip install https://github.com/z-mahmud22/Dlib_Windows_Python3.x/raw/main/dlib-19.22.99-cp311-cp311-win_amd64.whl
}

# Instalar dependências principais
Write-Host "`n📦 Instalando dependências..." -ForegroundColor Blue
python -m pip install -r requirements-windows.txt

# Testar importações
Write-Host "`n🧪 Testando importações..." -ForegroundColor Blue
python -c "
try:
    import fastapi, uvicorn, numpy, cv2, loguru, aiofiles
    print('✅ Dependências básicas OK!')
except ImportError as e:
    print(f'❌ Erro: {e}')

try:
    import face_recognition
    print('✅ face_recognition OK!')
except ImportError as e:
    print(f'⚠️  face_recognition falhou: {e}')
    print('💡 Use Docker para evitar problemas de dependências')
"

Write-Host "`n🎉 Instalação concluída!" -ForegroundColor Green
Write-Host "Para testar: python -m uvicorn app.main:app --reload" -ForegroundColor Cyan 