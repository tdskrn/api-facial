# 🔗 Integração Laravel - Comparação Direta de Imagens

## 📌 **Novo Fluxo Simplificado**

A API foi reformulada para receber **ambas as imagens** (referência + capturada) diretamente do Laravel, eliminando a necessidade de chamadas externas.

## 🔄 **Como Funciona Agora**

```
1. [Frontend] → [Laravel] → [API Flask]
   Captura foto + Employee ID

2. [Laravel] busca foto de referência no banco (base64)
   
3. [Laravel] → [API Flask]: 
   {
     "reference_image": "data:image/jpeg;base64,...",
     "captured_image": "data:image/jpeg;base64,...", 
     "employee_id": "123"
   }

4. [API Flask] compara as duas imagens

5. [API Flask] → [Laravel]:
   {
     "success": true,
     "match": true,
     "confidence": 0.92
   }

6. [Laravel] → [Frontend]: Resultado final
```

---

## 🛠️ **Implementação no Laravel**

### 1. **Modelo Employee**

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Employee extends Model
{
    protected $fillable = [
        'name',
        'email',
        'photo_base64',  // Campo para armazenar foto em base64
        'active'
    ];
    
    protected $casts = [
        'active' => 'boolean',
    ];
}
```

### 2. **Migration para Armazenar Base64**

```php
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up()
    {
        Schema::create('employees', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('email')->unique();
            $table->longText('photo_base64')->nullable(); // Para armazenar base64
            $table->boolean('active')->default(true);
            $table->timestamps();
        });
    }

    public function down()
    {
        Schema::dropIfExists('employees');
    }
};
```

### 3. **Controller para Validação Facial**

```php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Http;
use App\Models\Employee;

class FacialRecognitionController extends Controller
{
    /**
     * URL da API de reconhecimento facial
     */
    private string $facialApiUrl = 'https://sua-api-flask.com';
    
    /**
     * Valida funcionário usando reconhecimento facial
     */
    public function validateEmployee(Request $request): JsonResponse
    {
        try {
            $request->validate([
                'employee_id' => 'required|string',
                'captured_image' => 'required|string', // Base64 da foto capturada
            ]);
            
            $employeeId = $request->input('employee_id');
            $capturedImage = $request->input('captured_image');
            
            // Buscar funcionário no banco
            $employee = Employee::find($employeeId);
            
            if (!$employee) {
                return response()->json([
                    'success' => false,
                    'error' => 'Funcionário não encontrado',
                    'employee_id' => $employeeId
                ], 404);
            }
            
            if (!$employee->photo_base64) {
                return response()->json([
                    'success' => false,
                    'error' => 'Funcionário não possui foto cadastrada',
                    'employee_id' => $employeeId
                ], 404);
            }
            
            // Preparar dados para a API Flask
            $payload = [
                'reference_image' => $employee->photo_base64,
                'captured_image' => $capturedImage,
                'employee_id' => $employeeId
            ];
            
            // Chamar API de reconhecimento facial
            $response = Http::timeout(30)->post("{$this->facialApiUrl}/api/compare", $payload);
            
            if ($response->successful()) {
                $result = $response->json();
                
                // Log da validação
                \Log::info("Validação facial", [
                    'employee_id' => $employeeId,
                    'employee_name' => $employee->name,
                    'match' => $result['match'] ?? false,
                    'confidence' => $result['confidence'] ?? 0,
                    'success' => $result['success'] ?? false
                ]);
                
                return response()->json([
                    'success' => $result['success'] ?? false,
                    'match' => $result['match'] ?? false,
                    'confidence' => $result['confidence'] ?? 0,
                    'distance' => $result['distance'] ?? 0,
                    'threshold' => $result['threshold'] ?? 0.6,
                    'employee' => [
                        'id' => $employee->id,
                        'name' => $employee->name,
                        'email' => $employee->email
                    ]
                ]);
                
            } else {
                \Log::error("Erro na API de reconhecimento facial", [
                    'status' => $response->status(),
                    'body' => $response->body()
                ]);
                
                return response()->json([
                    'success' => false,
                    'error' => 'Erro na validação facial',
                    'details' => 'Serviço de reconhecimento indisponível'
                ], 500);
            }
            
        } catch (\Illuminate\Validation\ValidationException $e) {
            return response()->json([
                'success' => false,
                'error' => 'Dados inválidos',
                'details' => $e->errors()
            ], 422);
            
        } catch (\Exception $e) {
            \Log::error('Erro na validação facial: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Erro interno do servidor'
            ], 500);
        }
    }
    
    /**
     * Cadastra ou atualiza foto do funcionário
     */
    public function uploadPhoto(Request $request, $employeeId): JsonResponse
    {
        try {
            $request->validate([
                'photo' => 'required|image|mimes:jpeg,jpg,png|max:10240' // 10MB max
            ]);
            
            $employee = Employee::findOrFail($employeeId);
            
            // Converter imagem para base64
            $imageData = file_get_contents($request->file('photo')->path());
            $base64 = 'data:image/jpeg;base64,' . base64_encode($imageData);
            
            // Salvar no banco
            $employee->update(['photo_base64' => $base64]);
            
            return response()->json([
                'success' => true,
                'message' => 'Foto atualizada com sucesso',
                'employee_id' => $employeeId
            ]);
            
        } catch (\Exception $e) {
            \Log::error('Erro no upload de foto: ' . $e->getMessage());
            
            return response()->json([
                'success' => false,
                'error' => 'Erro no upload da foto'
            ], 500);
        }
    }
}
```

### 4. **Rotas**

```php
// routes/api.php
use App\Http\Controllers\FacialRecognitionController;

Route::prefix('facial')->group(function () {
    Route::post('/validate', [FacialRecognitionController::class, 'validateEmployee']);
    Route::post('/employee/{id}/photo', [FacialRecognitionController::class, 'uploadPhoto']);
});
```

---

## 📱 **Uso no Frontend**

### **JavaScript/Vue/React:**

```javascript
// Função para capturar foto da webcam e validar
async function validateEmployeeFacial(employeeId, photoBlob) {
    try {
        // Converter blob para base64
        const base64 = await blobToBase64(photoBlob);
        
        const response = await fetch('/api/facial/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                employee_id: employeeId,
                captured_image: base64
            })
        });
        
        const result = await response.json();
        
        if (result.success && result.match) {
            console.log(`✅ Funcionário ${result.employee.name} validado!`);
            console.log(`Confiança: ${(result.confidence * 100).toFixed(1)}%`);
            return true;
        } else {
            console.log(`❌ Validação falhou: ${result.error || 'Rosto não identificado'}`);
            return false;
        }
        
    } catch (error) {
        console.error('Erro na validação facial:', error);
        return false;
    }
}

// Função auxiliar para converter blob para base64
function blobToBase64(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = reject;
        reader.readAsDataURL(blob);
    });
}

// Exemplo de uso com webcam
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        const video = document.getElementById('webcam');
        video.srcObject = stream;
        
        // Capturar foto quando usuário clicar
        document.getElementById('capture').onclick = () => {
            const canvas = document.createElement('canvas');
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            
            const ctx = canvas.getContext('2d');
            ctx.drawImage(video, 0, 0);
            
            canvas.toBlob(blob => {
                validateEmployeeFacial('123', blob);
            }, 'image/jpeg', 0.8);
        };
    });
```

---

## 🧪 **Testando a Integração**

### **1. Testar API Flask diretamente:**

```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "reference_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
    "captured_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
    "employee_id": "123"
  }'
```

### **2. Testar no Laravel:**

```bash
curl -X POST http://localhost/api/facial/validate \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "123",
    "captured_image": "data:image/jpeg;base64,/9j/4AAQSkZ..."
  }'
```

---

## 📊 **Configuração da API Flask**

### **Arquivo .env:**

```bash
DEBUG=false
SECRET_KEY=sua-chave-secreta
PORT=8000
FACE_TOLERANCE=0.6
MAX_FILE_SIZE=20971520
```

### **Configuração do Nginx:**

```nginx
server {
    listen 80;
    server_name sua-api-flask.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Timeout aumentado para reconhecimento facial
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Tamanho máximo para duas imagens
        client_max_body_size 20M;
    }
}
```

---

## ✅ **Vantagens desta Abordagem**

1. **✅ Simplicidade**: Sem necessidade de autenticação entre APIs
2. **✅ Performance**: Uma única chamada HTTP
3. **✅ Controle**: Laravel gerencia ambas as imagens
4. **✅ Segurança**: Dados sensíveis não trafegam em URLs
5. **✅ Flexibilidade**: Fácil adicionar validações ou logs
6. **✅ Escalabilidade**: API Flask focada apenas em comparação

---

## 🚨 **Considerações Importantes**

### **Tamanho das Imagens:**
- Limite recomendado: 2MB por imagem (4MB total)
- Resolução recomendada: 800x600 pixels
- Formato preferido: JPEG com qualidade 80%

### **Performance:**
- Tempo médio de resposta: 2-5 segundos
- Concorrência recomendada: 10 requests simultâneos
- Cache no Laravel para evitar recálculos

### **Segurança:**
- Validar formato das imagens
- Limitar tamanho dos requests
- Rate limiting no Nginx
- HTTPS obrigatório em produção

---

## 📋 **Checklist de Implementação**

- [ ] Migration criada com campo `photo_base64`
- [ ] Modelo `Employee` atualizado
- [ ] Controller `FacialRecognitionController` criado
- [ ] Rotas configuradas
- [ ] API Flask atualizada e funcionando
- [ ] Nginx configurado com limits apropriados
- [ ] Frontend implementado com captura de webcam
- [ ] Testes realizados com sucesso
- [ ] Logs configurados para auditoria
- [ ] HTTPS configurado em produção

Agora o Laravel envia **ambas as imagens** para nossa API e recebe apenas o resultado da comparação! 🎉