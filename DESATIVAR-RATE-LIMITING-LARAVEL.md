# 🚫 Como Desativar Rate Limiting no Laravel

## 🔍 Problema Identificado

Você está recebendo o erro **HTTP 429** com a mensagem:
```json
{
  "success": false,
  "message": "Padrão suspeito detectado. Tente novamente em alguns minutos.",
  "code": "SUSPICIOUS_PATTERN"
}
```

Este erro indica que o **Rate Limiting** (limitação de taxa) está ativo na API Laravel.

---

## 🎯 Soluções para Desativar Rate Limiting

### **1. Verificar Middleware de Throttle**

#### **Localizar o Middleware:**
```bash
# Procurar por throttle nos arquivos de rota
grep -r "throttle" routes/
grep -r "RateLimiter" app/
```

#### **Arquivo: `routes/api.php`**
```php
// ❌ PROBLEMA: Rate limiting ativo
Route::middleware(['throttle:60,1'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
});

// ✅ SOLUÇÃO: Remover throttle
Route::group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
});
```

### **2. Configurar Rate Limiting Personalizado**

#### **Arquivo: `app/Providers/RouteServiceProvider.php`**
```php
use Illuminate\Cache\RateLimiting\Limit;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\RateLimiter;

public function boot()
{
    // ❌ PROBLEMA: Limite muito restritivo
    RateLimiter::for('api', function (Request $request) {
        return Limit::perMinute(60)->by($request->user()?->id ?: $request->ip());
    });
    
    // ✅ SOLUÇÃO 1: Aumentar limite drasticamente
    RateLimiter::for('api', function (Request $request) {
        return Limit::perMinute(10000)->by($request->user()?->id ?: $request->ip());
    });
    
    // ✅ SOLUÇÃO 2: Desativar completamente
    RateLimiter::for('api', function (Request $request) {
        return Limit::none(); // Sem limite
    });
}
```

### **3. Remover Middleware Throttle das Rotas**

#### **Arquivo: `routes/api.php`**
```php
// ❌ ANTES: Com throttle
Route::middleware(['api', 'throttle:api'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
    Route::post('/auth/register', [AuthController::class, 'register']);
});

// ✅ DEPOIS: Sem throttle
Route::middleware(['api'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
    Route::post('/auth/register', [AuthController::class, 'register']);
});

// ✅ OU: Completamente sem middleware
Route::post('/auth/login', [AuthController::class, 'login']);
Route::post('/auth/register', [AuthController::class, 'register']);
```

### **4. Verificar Middleware Global**

#### **Arquivo: `app/Http/Kernel.php`**
```php
protected $middlewareGroups = [
    'api' => [
        // ❌ PROBLEMA: Throttle no grupo API
        'throttle:api',
        \Illuminate\Routing\Middleware\SubstituteBindings::class,
    ],
];

// ✅ SOLUÇÃO: Remover throttle
protected $middlewareGroups = [
    'api' => [
        \Illuminate\Routing\Middleware\SubstituteBindings::class,
    ],
];
```

### **5. Configuração Específica para Login**

#### **Criar Rate Limiter Específico:**
```php
// app/Providers/RouteServiceProvider.php
public function boot()
{
    // Rate limiter específico para login (mais permissivo)
    RateLimiter::for('login', function (Request $request) {
        return [
            Limit::perMinute(100)->by($request->ip()),
            Limit::perMinute(50)->by($request->input('email')),
        ];
    });
    
    // OU: Sem limite para login
    RateLimiter::for('login', function (Request $request) {
        return Limit::none();
    });
}
```

#### **Aplicar nas Rotas:**
```php
// routes/api.php
Route::post('/auth/login', [AuthController::class, 'login'])
    ->middleware('throttle:login'); // Usar rate limiter específico

// OU: Sem throttle
Route::post('/auth/login', [AuthController::class, 'login']);
```

---

## 🔧 Implementação Passo a Passo

### **Passo 1: Identificar o Problema**
```bash
# Verificar rotas com throttle
php artisan route:list | grep throttle

# Verificar configuração atual
grep -r "throttle" routes/ app/
```

### **Passo 2: Backup dos Arquivos**
```bash
cp routes/api.php routes/api.php.backup
cp app/Http/Kernel.php app/Http/Kernel.php.backup
cp app/Providers/RouteServiceProvider.php app/Providers/RouteServiceProvider.php.backup
```

### **Passo 3: Aplicar Correção**

#### **Opção A: Remover Completamente (Desenvolvimento)**
```php
// routes/api.php
// Remover 'throttle:api' de todas as rotas
Route::middleware(['api'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
    // ... outras rotas
});
```

#### **Opção B: Aumentar Limite (Produção)**
```php
// app/Providers/RouteServiceProvider.php
RateLimiter::for('api', function (Request $request) {
    return Limit::perMinute(1000)->by($request->user()?->id ?: $request->ip());
});
```

### **Passo 4: Limpar Cache**
```bash
php artisan route:clear
php artisan config:clear
php artisan cache:clear
```

### **Passo 5: Testar**
```bash
# Testar endpoint de login
curl -X POST https://diasadvogado.com.br/ponto/api/auth/login \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"email":"teste@teste.com","password":"senha123"}'
```

---

## 🛡️ Configurações de Segurança Alternativas

### **1. Rate Limiting Inteligente**
```php
// app/Providers/RouteServiceProvider.php
RateLimiter::for('smart-login', function (Request $request) {
    // Limite por IP
    $ipLimit = Limit::perMinute(100)->by($request->ip());
    
    // Limite por email (mais restritivo)
    $emailLimit = Limit::perMinute(20)->by($request->input('email'));
    
    return [$ipLimit, $emailLimit];
});
```

### **2. Whitelist de IPs**
```php
// app/Http/Middleware/CustomThrottle.php
public function handle($request, Closure $next, ...$limits)
{
    $whitelistedIPs = [
        '192.168.1.100', // IP do desenvolvedor
        '10.0.0.0/8',    // Rede interna
    ];
    
    if (in_array($request->ip(), $whitelistedIPs)) {
        return $next($request); // Pular throttle
    }
    
    return app(ThrottleRequests::class)->handle($request, $next, ...$limits);
}
```

### **3. Throttle Baseado em Usuário**
```php
RateLimiter::for('user-based', function (Request $request) {
    if ($request->user()) {
        // Usuários autenticados: limite maior
        return Limit::perMinute(500)->by($request->user()->id);
    }
    
    // Usuários anônimos: limite menor
    return Limit::perMinute(50)->by($request->ip());
});
```

---

## 🚨 Considerações de Segurança

### **⚠️ Riscos de Desativar Rate Limiting:**
1. **Ataques de Força Bruta**: Login sem proteção
2. **DDoS**: Sobrecarga do servidor
3. **Spam**: Requisições excessivas

### **✅ Alternativas Seguras:**
1. **Aumentar limite** em vez de desativar
2. **Whitelist de IPs** confiáveis
3. **Rate limiting inteligente** por usuário
4. **Captcha** após tentativas falhadas

---

## 🔍 Debug e Monitoramento

### **1. Log de Rate Limiting**
```php
// app/Providers/RouteServiceProvider.php
RateLimiter::for('api', function (Request $request) {
    \Log::info('Rate limit check', [
        'ip' => $request->ip(),
        'user_id' => $request->user()?->id,
        'endpoint' => $request->path(),
    ]);
    
    return Limit::perMinute(1000)->by($request->ip());
});
```

### **2. Headers de Debug**
```php
// Verificar headers de rate limiting na resposta
// X-RateLimit-Limit: 60
// X-RateLimit-Remaining: 59
// Retry-After: 60
```

### **3. Comando de Teste**
```bash
# Testar múltiplas requisições
for i in {1..10}; do
  curl -X POST https://diasadvogado.com.br/ponto/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"email":"teste@teste.com","password":"senha123"}' \
    -w "Status: %{http_code}\n"
  sleep 1
done
```

---

## ✅ Solução Rápida (Desenvolvimento)

### **Para resolver IMEDIATAMENTE:**

1. **Editar `routes/api.php`:**
```php
// Comentar ou remover 'throttle:api'
Route::middleware(['api'])->group(function () {
    Route::post('/auth/login', [AuthController::class, 'login']);
});
```

2. **Limpar cache:**
```bash
php artisan route:clear
php artisan config:clear
```

3. **Testar novamente no Flutter**

### **Para Produção:**

1. **Aumentar limite em `RouteServiceProvider.php`:**
```php
RateLimiter::for('api', function (Request $request) {
    return Limit::perMinute(1000)->by($request->ip());
});
```

2. **Aplicar e testar**

---

## 📞 Próximos Passos

1. ✅ **Identificar** onde está o throttle
2. ✅ **Fazer backup** dos arquivos
3. ✅ **Aplicar correção** (remover ou aumentar limite)
4. ✅ **Limpar cache** do Laravel
5. ✅ **Testar** no Flutter
6. ✅ **Monitorar** logs de acesso

**Resultado esperado**: Erro 429 deve desaparecer e login deve funcionar normalmente! 🎯