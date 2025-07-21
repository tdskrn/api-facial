# 🔗 Integração Flask + Laravel - Guia Completo

## 📌 Como Funciona Agora

A API Flask foi adaptada para **buscar as fotos de referência diretamente da sua API Laravel**, ao invés de usar URLs estáticas. O fluxo agora é:

1. **Frontend** envia foto capturada + employee_id para **API Flask**
2. **API Flask** faz chamada para **API Laravel** buscando a foto de referência
3. **API Laravel** retorna URL da foto do funcionário
4. **API Flask** baixa a foto e faz a comparação facial
5. **API Flask** retorna resultado da comparação

## 🔄 Fluxo de Dados

```
[Frontend] 
    ↓ POST /api/validate
    ↓ {employee_id: "123", image_base64: "..."}
    ↓
[API Flask]
    ↓ GET /api/employee/123/photo
    ↓ Authorization: Bearer token
    ↓
[API Laravel]
    ↓ Response: {photo_url: "https://..."}
    ↓
[API Flask] ← Downloads image and compares
    ↓
[Frontend] ← {success: true, match: true, confidence: 0.92}
```

## 🛠️ Configuração da API Laravel

### 1. Criar Controller

Crie `app/Http/Controllers/EmployeeController.php`:

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use App\Models\Employee;

class EmployeeController extends Controller
{
    public function getPhoto($id): JsonResponse
    {
        try {
            $employee = Employee::find($id);
            
            if (!$employee) {
                return response()->json([
                    'error' => 'Funcionário não encontrado',
                    'employee_id' => $id
                ], 404);
            }
            
            if (!$employee->photo_path) {
                return response()->json([
                    'error' => 'Funcionário não possui foto cadastrada',
                    'employee_id' => $id
                ], 404);
            }
            
            $photoUrl = asset('storage/' . $employee->photo_path);
            
            return response()->json([
                'success' => true,
                'employee_id' => $id,
                'employee_name' => $employee->name,
                'photo_url' => $photoUrl,
                'updated_at' => $employee->updated_at
            ]);
            
        } catch (\Exception $e) {
            \Log::error('Erro ao buscar foto: ' . $e->getMessage());
            
            return response()->json([
                'error' => 'Erro interno do servidor',
                'employee_id' => $id
            ], 500);
        }
    }
}
```

### 2. Configurar Rotas

Em `routes/api.php`:

```php
use App\Http\Controllers\EmployeeController;

Route::middleware('auth:sanctum')->group(function () {
    Route::get('/employee/{id}/photo', [EmployeeController::class, 'getPhoto']);
});
```

### 3. Modelo Employee

Certifique-se de que o modelo `Employee` tem:

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Employee extends Model
{
    protected $fillable = [
        'name',
        'email', 
        'photo_path',  // Caminho: "employees/123.jpg"
        'active'
    ];
    
    protected $casts = [
        'active' => 'boolean'
    ];
}
```

### 4. Gerar Token de API

No seu Laravel, gere um token para autenticação:

```php
// No tinker ou controller
$user = User::find(1); // Usuário admin
$token = $user->createToken('facial-api')->plainTextToken;
echo $token; // Use este token na configuração
```

## ⚙️ Configuração da API Flask

### 1. Arquivo .env

Crie/edite o arquivo `.env`:

```bash
# Configurações básicas
DEBUG=false
SECRET_KEY=sua-chave-secreta-super-forte-aqui
PORT=8000

# Integração Laravel (OBRIGATÓRIO)
LARAVEL_API_BASE=https://meusite-laravel.com.br
LARAVEL_API_TOKEN=1|abc123def456...

# Reconhecimento facial
FACE_TOLERANCE=0.6
MAX_FILE_SIZE=10485760
```

### 2. Estrutura de Dados

**Requisição para API Flask:**
```json
POST /api/validate
Content-Type: application/json

{
    "employee_id": "123",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZ..."
}
```

**API Laravel deve responder:**
```json
GET /api/employee/123/photo
Authorization: Bearer 1|abc123...

{
    "success": true,
    "employee_id": "123",
    "employee_name": "João Silva",
    "photo_url": "https://meusite.com.br/storage/employees/123.jpg",
    "updated_at": "2024-01-15T10:30:00.000000Z"
}
```

**Resposta da API Flask:**
```json
{
    "success": true,
    "match": true,
    "confidence": 0.92,
    "distance": 0.08,
    "threshold": 0.6
}
```

## 🧪 Testando a Integração

### 1. Teste Básico

```bash
# Testar API Flask
python3 test-laravel-integration.py
```

### 2. Teste Manual da API Laravel

```bash
# Teste se sua API Laravel responde
curl -H "Authorization: Bearer SEU_TOKEN" \
     -H "Accept: application/json" \
     https://meusite-laravel.com.br/api/employee/123/photo
```

### 3. Teste Completo

```bash
# Teste validação facial completa
curl -X POST http://localhost:8000/api/validate \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "123",
    "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZ..."
  }'
```

## 🚨 Resolução de Problemas

### Erro: "Funcionário não encontrado"

**Causa:** API Laravel retornou 404
**Solução:** 
- Verificar se employee_id existe no banco
- Verificar se o endpoint `/api/employee/{id}/photo` existe
- Testar diretamente a API Laravel

### Erro: "Não autorizado"

**Causa:** Token inválido ou expirado
**Solução:**
- Gerar novo token no Laravel
- Verificar se token está correto no `.env`
- Verificar middleware `auth:sanctum`

### Erro: "Não foi possível carregar imagem"

**Causa:** URL da foto inválida ou arquivo não existe
**Solução:**
- Verificar se `photo_path` está correto no banco
- Verificar se arquivo existe em `storage/app/public/`
- Testar URL da foto no navegador

### Erro: "Nenhum rosto encontrado"

**Causa:** Imagem sem rosto detectável
**Solução:**
- Verificar qualidade da foto de referência
- Garantir que foto tem pelo menos 50x50 pixels
- Testar com foto de melhor qualidade

## 📱 Integração no Frontend

### JavaScript/React exemplo:

```javascript
async function validateEmployee(employeeId, capturedImageBase64) {
    try {
        const response = await fetch('https://sua-api-flask.com/api/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                employee_id: employeeId,
                image_base64: capturedImageBase64
            })
        });
        
        const result = await response.json();
        
        if (result.success && result.match) {
            console.log(`✅ Funcionário validado! Confiança: ${result.confidence}`);
            return true;
        } else {
            console.log(`❌ Validação falhou: ${result.reason || 'Não identificado'}`);
            return false;
        }
        
    } catch (error) {
        console.error('Erro na validação:', error);
        return false;
    }
}

// Uso
const isValid = await validateEmployee('123', 'data:image/jpeg;base64,...');
```

### PHP/Laravel exemplo:

```php
use Illuminate\Support\Facades\Http;

public function validateFacialRecognition($employeeId, $imageBase64)
{
    try {
        $response = Http::timeout(30)->post('https://sua-api-flask.com/api/validate', [
            'employee_id' => $employeeId,
            'image_base64' => $imageBase64
        ]);
        
        if ($response->successful()) {
            $result = $response->json();
            
            if ($result['success'] && $result['match']) {
                // Log do sucesso
                Log::info("Validação facial sucesso para funcionário {$employeeId}", [
                    'confidence' => $result['confidence'],
                    'distance' => $result['distance']
                ]);
                
                return [
                    'valid' => true,
                    'confidence' => $result['confidence']
                ];
            }
        }
        
        return ['valid' => false, 'reason' => $result['reason'] ?? 'Falha na validação'];
        
    } catch (\Exception $e) {
        Log::error("Erro na validação facial: " . $e->getMessage());
        return ['valid' => false, 'reason' => 'Erro de comunicação'];
    }
}
```

## 🔧 Deploy em Produção

### 1. Configure SSL no Laravel

Certifique-se de que sua API Laravel tem HTTPS configurado.

### 2. Configure CORS

No Laravel, configure CORS para permitir sua API Flask:

```php
// config/cors.php
'allowed_origins' => [
    'https://sua-api-flask.com'
],
```

### 3. Configure Rate Limiting

Proteja sua API Laravel contra spam:

```php
// routes/api.php
Route::middleware(['auth:sanctum', 'throttle:60,1'])->group(function () {
    Route::get('/employee/{id}/photo', [EmployeeController::class, 'getPhoto']);
});
```

## 📊 Monitoramento

### Logs Importantes

**API Flask:**
```bash
tail -f /var/www/facial-api/logs/api.log
```

**API Laravel:**
```bash
tail -f storage/logs/laravel.log
```

### Métricas de Performance

- **Tempo médio de resposta**: < 3 segundos
- **Taxa de sucesso**: > 95%
- **Accuracy**: > 90% (com fotos de boa qualidade)

## ✅ Checklist de Configuração

- [ ] API Laravel respondendo em `/api/employee/{id}/photo`
- [ ] Token Sanctum gerado e configurado
- [ ] Fotos dos funcionários acessíveis via URL
- [ ] `.env` da API Flask configurado
- [ ] Teste `python3 test-laravel-integration.py` passando
- [ ] HTTPS configurado em produção
- [ ] CORS configurado
- [ ] Rate limiting ativo

Agora sua API Flask busca as fotos diretamente do Laravel! 🎉