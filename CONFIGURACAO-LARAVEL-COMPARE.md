# 🔧 Configuração Laravel para Rota `/api/compare`

## 📋 Análise do Código Laravel

Seu código Laravel está correto e já está configurado para usar a rota `/api/compare`. Vou explicar como garantir que tudo funcione perfeitamente.

## ⚙️ Configurações Necessárias

### 1. **Arquivo `.env` do Laravel**

Adicione/configure estas variáveis no seu `.env`:

```env
# URL do microserviço de reconhecimento facial (API rodando na porta 8000)
FACE_MICROSERVICE_URL=http://arcanun-tech.vps-kinghost.net:8000

# Timeout para requisições (em segundos)
FACE_MICROSERVICE_TIMEOUT=30

# Threshold padrão para validação facial (0.0 a 1.0)
FACE_VALIDATION_DEFAULT_THRESHOLD=0.6
```

### 2. **Arquivo `config/app.php`**

Adicione as configurações:

```php
<?php

return [
    // ... outras configurações
    
    /*
    |--------------------------------------------------------------------------
    | Face Recognition Microservice Configuration
    |--------------------------------------------------------------------------
    */
    'face_microservice_url' => env('FACE_MICROSERVICE_URL', 'http://localhost:5000'),
    'face_microservice_timeout' => env('FACE_MICROSERVICE_TIMEOUT', 30),
    'face_validation_default_threshold' => env('FACE_VALIDATION_DEFAULT_THRESHOLD', 0.6),
];
```

## 🎯 Verificação da API Flask

### **Confirmar se a API Flask está rodando:**

```bash
# Testar se a API está respondendo
curl http://arcanun-tech.vps-kinghost.net:8000/

# Testar health check
curl http://arcanun-tech.vps-kinghost.net:8000/health

# Testar endpoint compare (com dados de exemplo)
curl -X POST http://arcanun-tech.vps-kinghost.net:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "reference_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "captured_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "employee_id": "123"
  }'
```

## 🔧 Ajustes no Código Laravel

### **Seu código está correto, mas aqui estão algumas melhorias:**

```php
public function compareWithMicroservice(Request $request): JsonResponse 
{ 
    try { 
        // Validação híbrida: aceita campos de validação facial + registro de ponto 
        $validated = $request->validate([ 
            'photo_current' => 'required|string', 
            'user_id' => 'required|integer|exists:users,id', 
            'threshold' => 'nullable|numeric|min:0|max:1', 
            // Campos adicionais para registro de ponto (enviados pelo Flutter) 
            'tipo' => 'nullable|in:entrada,saida', 
            'latitude' => 'nullable|numeric', 
            'longitude' => 'nullable|numeric', 
            'observacoes' => 'nullable|string|max:500', 
        ]); 

        $user = User::find($validated['user_id']); 
        if (!$user || !$user->foto) { 
            return response()->json([ 
                'success' => false, 
                'message' => 'Usuário ou foto de referência não encontrada' 
            ], 404); 
        } 

        // ✅ CONFIGURAÇÃO CORRETA DA API (porta 8000)
        $microserviceUrl = config('app.face_microservice_url', 'http://arcanun-tech.vps-kinghost.net:8000'); 
        $timeout = config('app.face_microservice_timeout', 30); 
        $defaultThreshold = config('app.face_validation_default_threshold', 0.6); 

        // ✅ PAYLOAD CORRETO PARA /api/compare
        $microservicePayload = [ 
            'reference_image' => $user->foto, // Deve estar em formato base64 com prefixo
            'captured_image' => $validated['photo_current'], // Deve estar em formato base64 com prefixo
            'employee_id' => (string) $validated['user_id'] 
        ]; 

        // ✅ CHAMADA CORRETA PARA /api/compare
        Log::info('Tentando validação facial com API', [ 
            'user_id' => $validated['user_id'], 
            'microservice_url' => $microserviceUrl, 
            'endpoint' => '/api/compare',
            'timeout' => $timeout 
        ]); 

        $response = Http::timeout($timeout) 
            ->withHeaders(['Content-Type' => 'application/json']) 
            ->post("{$microserviceUrl}/api/compare", $microservicePayload); 

        if (!$response->successful()) { 
            Log::error('API retornou erro', [ 
                'user_id' => $validated['user_id'], 
                'status' => $response->status(), 
                'body' => $response->body(), 
                'microservice_url' => $microserviceUrl,
                'endpoint' => '/api/compare'
            ]); 

            return response()->json([ 
                'success' => false, 
                'message' => 'Erro no microserviço de validação facial', 
                'error_details' => [ 
                    'status' => $response->status(), 
                    'response' => $response->body(), 
                    'microservice_url' => $microserviceUrl 
                ] 
            ], 500); 
        } 

        $faceValidationResult = $response->json(); 
         
        // ✅ PROCESSAMENTO CORRETO DA RESPOSTA
        $isValid = $faceValidationResult['success'] && $faceValidationResult['match']; 
        $confidence = $faceValidationResult['confidence'] ?? 0; 
        $threshold = $validated['threshold'] ?? $defaultThreshold; 
         
        // Aplicar threshold customizado se fornecido 
        if (isset($validated['threshold'])) { 
            $isValid = $faceValidationResult['success'] && $confidence >= $threshold; 
        } 

        Log::info('Validação facial via API concluída', [ 
            'user_id' => $validated['user_id'], 
            'confidence' => $confidence, 
            'match' => $faceValidationResult['match'] ?? false, 
            'is_valid' => $isValid, 
            'threshold_used' => $threshold,
            'distance' => $faceValidationResult['distance'] ?? null
        ]); 

        // ... resto do código para registro de ponto permanece igual
        
        return response()->json([
            'success' => $isValid,
            'message' => $isValid ? 'Validação facial aprovada' : 'Validação facial rejeitada',
            'data' => [
                'face_validation' => [
                    'match' => $faceValidationResult['match'] ?? false,
                    'confidence' => $confidence,
                    'distance' => $faceValidationResult['distance'] ?? null,
                    'threshold' => $threshold
                ],
                'registro' => $registroData
            ]
        ]);
        
    } catch (Exception $e) {
        Log::error('Erro na validação facial', [
            'user_id' => $validated['user_id'] ?? null,
            'error' => $e->getMessage(),
            'trace' => $e->getTraceAsString()
        ]);
        
        return response()->json([
            'success' => false,
            'message' => 'Erro interno na validação facial'
        ], 500);
    }
}
```

## 🚨 Pontos Importantes

### **1. Formato das Imagens**
As imagens devem estar em formato base64 com prefixo:
```
data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...
```

### **2. Porta da API**
A API com a rota `/api/compare` roda na **porta 8000**:
- ✅ Correto: `http://arcanun-tech.vps-kinghost.net:8000/api/compare`
- ❌ Errado: `http://arcanun-tech.vps-kinghost.net:5000/api/compare`

### **3. Resposta da API**
A API `/api/compare` retorna:
```json
{
  "success": true,
  "match": true,
  "confidence": 0.92,
  "distance": 0.08,
  "threshold": 0.6
}
```

## 🧪 Teste Completo

### **Script de Teste Laravel:**

```php
// routes/web.php ou routes/api.php
Route::post('/test-face-compare', function (Request $request) {
    $testPayload = [
        'reference_image' => 'data:image/jpeg;base64,' . base64_encode(file_get_contents('path/to/reference.jpg')),
        'captured_image' => 'data:image/jpeg;base64,' . base64_encode(file_get_contents('path/to/captured.jpg')),
        'employee_id' => '123'
    ];
    
    $response = Http::timeout(30)
        ->post('http://arcanun-tech.vps-kinghost.net:8000/api/compare', $testPayload);
    
    return response()->json([
        'status' => $response->status(),
        'response' => $response->json()
    ]);
});
```

## ✅ Checklist de Verificação

- [ ] Variáveis de ambiente configuradas no `.env`
- [ ] Configurações adicionadas em `config/app.php`
- [ ] API rodando na porta 8000
- [ ] Endpoint `/api/compare` acessível
- [ ] Imagens em formato base64 com prefixo correto
- [ ] Logs configurados para debug
- [ ] Timeout adequado (30 segundos)

## 🎯 Conclusão

Seu código Laravel está **correto** e já está configurado para usar a rota `/api/compare`. Apenas certifique-se de que:

1. **A API está rodando na porta 8000** (não na 5000 como inicialmente pensado)
2. **As configurações estão no `.env` e `config/app.php`** com a URL correta
3. **As imagens estão em formato base64 correto**

✅ **CONFIRMADO**: A rota `/api/compare` está **funcionando** em `http://arcanun-tech.vps-kinghost.net:8000/api/compare`

A integração deve funcionar perfeitamente com essas configurações!