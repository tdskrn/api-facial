# 📊 Explicação da Rota `/api/compare`

## 🔍 Análise dos Logs do Gunicorn

Baseado nos logs fornecidos, você tem duas APIs diferentes rodando:

### 📋 Logs Analisados:
```
Jul 21 22:08:29 - POST /boaform/admin/formLogin - Status: 404
Jul 21 22:12:43 - GET / - Status: 200
Jul 21 22:14:15 - GET /login.rsp - Status: 404
Jul 21 22:16:29 - GET / - Status: 200
Jul 21 22:25:08 - GET / - Status: 200
```

## 🎯 Como Funciona a Rota `/api/compare`

### 📍 **Localização**: Flask API (`app.py`)
A rota `/api/compare` está implementada em uma **API Flask separada** da API FastAPI principal.

### 🔧 **Funcionalidade**:
Realiza comparação facial **direta** entre duas imagens em formato base64.

### 📨 **Endpoint**:
```
POST /api/compare
Content-Type: application/json
```

### 📋 **Payload de Entrada**:
```json
{
  "reference_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
  "captured_image": "data:image/jpeg;base64,/9j/4AAQSkZ...",
  "employee_id": "123" // Opcional, apenas para log
}
```

### 📤 **Resposta de Sucesso**:
```json
{
  "success": true,
  "match": true,
  "confidence": 0.92,
  "distance": 0.08,
  "threshold": 0.6
}
```

### ❌ **Resposta de Erro**:
```json
{
  "success": false,
  "error": "Descrição do erro",
  "details": "Detalhes técnicos (apenas em modo DEBUG)"
}
```

## 🔄 **Processo de Comparação**:

1. **Validação**: Verifica se o request é JSON válido
2. **Campos Obrigatórios**: Valida `reference_image` e `captured_image`
3. **Formato Base64**: Confirma formato `data:image/...;base64,...`
4. **Comparação Facial**: Usa `compare_two_images()` do módulo `face_matcher`
5. **Log de Resultado**: Registra match/no-match com confiança e distância
6. **Resposta JSON**: Retorna resultado estruturado

## ⚙️ **Configurações**:

- **Tolerância Facial**: `FACE_TOLERANCE=0.6` (padrão)
- **Tamanho Máximo**: 20MB (para duas imagens)
- **Porta**: 5000 (Flask) vs 8000 (FastAPI)
- **Debug Mode**: Controlado por variável de ambiente

## 🆚 **Diferenças entre APIs**:

| Aspecto | Flask API (`app.py`) | FastAPI (`main.py`) |
|---------|---------------------|--------------------|
| **Porta** | 5000 | 8000 |
| **Função** | Comparação direta | Sistema completo |
| **Endpoint** | `/api/compare` | `/api/v1/verify-face/{id}` |
| **Entrada** | 2 imagens base64 | 1 imagem + ID funcionário |
| **Armazenamento** | Não armazena | Armazena fotos cadastradas |
| **Uso** | Comparação pontual | Sistema de ponto |

## 🧪 **Teste da Rota Compare**:

### Usando cURL:
```bash
curl -X POST http://localhost:5000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "reference_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "captured_image": "data:image/jpeg;base64,/9j/4AAQ...",
    "employee_id": "123"
  }'
```

### Usando PHP (Laravel):
```php
$response = Http::timeout(30)->post('http://localhost:5000/api/compare', [
    'reference_image' => 'data:image/jpeg;base64,' . base64_encode($referenceImage),
    'captured_image' => 'data:image/jpeg;base64,' . base64_encode($capturedImage),
    'employee_id' => $employeeId
]);

$result = $response->json();
if ($result['success'] && $result['match']) {
    // Rosto corresponde
    $confidence = $result['confidence'];
}
```

## 📊 **Logs Esperados**:

Quando a rota `/api/compare` é chamada, você verá logs como:
```
📨 Comparação facial solicitada para funcionário: 123
🎯 Resultado para 123: ✅ MATCH (confiança: 0.920, distância: 0.0800)
```

## 🚨 **Possíveis Problemas**:

1. **404 nos logs**: As rotas `/boaform/admin/formLogin` e `/login.rsp` não existem
2. **API Flask vs FastAPI**: Certifique-se de usar a porta correta (5000 vs 8000)
3. **Formato Base64**: Imagens devem incluir o prefixo `data:image/...;base64,`
4. **Tamanho**: Máximo 20MB total (duas imagens)

## 🎯 **Conclusão**:

A rota `/api/compare` é uma **API Flask independente** para comparação facial direta entre duas imagens, diferente da API FastAPI principal que gerencia um sistema completo de reconhecimento facial com armazenamento de funcionários.

**Para usar a rota compare**: Acesse `http://seu-servidor:5000/api/compare`
**Para usar o sistema completo**: Acesse `http://seu-servidor:8000/api/v1/verify-face/{employee_id}`