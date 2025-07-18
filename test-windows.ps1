# Script de teste para Windows PowerShell
Write-Host "🎯 Testando API de Reconhecimento Facial" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$API_URL = "http://localhost:8000"
$EMPLOYEE_ID = "123"

# Função para testar endpoint
function Test-Endpoint {
    param($Method, $Url, $Description)
    
    Write-Host "`n🧪 Testando: $Description" -ForegroundColor Blue
    Write-Host "   → $Method $Url" -ForegroundColor Gray
    
    try {
        $response = Invoke-WebRequest -Uri $Url -Method $Method -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "   ✅ Sucesso" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️ Status: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "   ❌ Falhou: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Testar endpoints básicos
Write-Host "`n📋 TESTANDO ENDPOINTS BÁSICOS" -ForegroundColor Cyan
Test-Endpoint "GET" "$API_URL/" "Endpoint raiz"
Test-Endpoint "GET" "$API_URL/health" "Health check global"
Test-Endpoint "GET" "$API_URL/api/v1/health" "Health check API facial"
Test-Endpoint "GET" "$API_URL/api/v1/statistics" "Estatísticas do sistema"

# Testar gestão de funcionários
Write-Host "`n👤 TESTANDO GESTÃO DE FUNCIONÁRIOS" -ForegroundColor Cyan
Test-Endpoint "GET" "$API_URL/api/v1/employee/$EMPLOYEE_ID/status" "Status do funcionário $EMPLOYEE_ID"

# Teste com arquivo (se existir)
Write-Host "`n📷 TESTE DE UPLOAD" -ForegroundColor Cyan
Write-Host "Para testar upload de foto:" -ForegroundColor Yellow
Write-Host "1. Coloque uma foto chamada 'test.jpg' nesta pasta" -ForegroundColor Yellow
Write-Host "2. Execute:" -ForegroundColor Yellow
Write-Host "   Test-Upload" -ForegroundColor Gray

function Test-Upload {
    if (Test-Path "test.jpg") {
        Write-Host "`n📷 Testando upload..." -ForegroundColor Blue
        try {
            $form = @{
                file = Get-Item "test.jpg"
            }
            $response = Invoke-WebRequest -Uri "$API_URL/api/v1/register-employee/123" -Method Post -Form $form
            Write-Host "✅ Upload sucesso!" -ForegroundColor Green
            Write-Host "Resposta: $($response.Content)" -ForegroundColor Gray
        } catch {
            Write-Host "❌ Upload falhou: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "⚠️ Arquivo 'test.jpg' não encontrado" -ForegroundColor Yellow
    }
}

Write-Host "`n🌐 INFORMAÇÕES ÚTEIS" -ForegroundColor Cyan
Write-Host "• Documentação: $API_URL/docs" -ForegroundColor White
Write-Host "• API Base: $API_URL" -ForegroundColor White
Write-Host "• Health Check: $API_URL/health" -ForegroundColor White
Write-Host "• Estatísticas: $API_URL/api/v1/statistics" -ForegroundColor White

Write-Host "`n✅ Teste concluído!" -ForegroundColor Green 