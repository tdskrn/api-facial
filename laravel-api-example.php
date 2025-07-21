<?php
// 📋 Exemplo de implementação da API Laravel
// Salve este código no seu projeto Laravel

// routes/api.php
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/employee/{id}/photo', [EmployeeController::class, 'getPhoto']);
});

// app/Http/Controllers/EmployeeController.php
<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use App\Models\Employee;

class EmployeeController extends Controller
{
    /**
     * Retorna a URL da foto do funcionário para reconhecimento facial
     * 
     * @param string $id ID do funcionário
     * @return JsonResponse
     */
    public function getPhoto($id): JsonResponse
    {
        try {
            // Buscar funcionário no banco de dados
            $employee = Employee::find($id);
            
            if (!$employee) {
                return response()->json([
                    'error' => 'Funcionário não encontrado',
                    'employee_id' => $id
                ], 404);
            }
            
            // Verificar se o funcionário tem foto
            if (!$employee->photo || !$employee->photo_path) {
                return response()->json([
                    'error' => 'Funcionário não possui foto cadastrada',
                    'employee_id' => $id
                ], 404);
            }
            
            // Construir URL completa da foto
            $photoUrl = asset('storage/' . $employee->photo_path);
            
            // Verificar se arquivo existe fisicamente
            $photoPath = storage_path('app/public/' . $employee->photo_path);
            if (!file_exists($photoPath)) {
                return response()->json([
                    'error' => 'Arquivo de foto não encontrado no servidor',
                    'employee_id' => $id
                ], 404);
            }
            
            return response()->json([
                'success' => true,
                'employee_id' => $id,
                'employee_name' => $employee->name,
                'photo_url' => $photoUrl,  // URL que nossa API Flask irá baixar
                'photo_size' => filesize($photoPath),
                'updated_at' => $employee->updated_at
            ]);
            
        } catch (\Exception $e) {
            \Log::error('Erro ao buscar foto do funcionário: ' . $e->getMessage());
            
            return response()->json([
                'error' => 'Erro interno do servidor',
                'employee_id' => $id
            ], 500);
        }
    }
}

// app/Models/Employee.php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Employee extends Model
{
    protected $fillable = [
        'name',
        'email',
        'photo_path',  // Caminho da foto (ex: "employees/123.jpg")
        'active'
    ];
    
    protected $casts = [
        'active' => 'boolean',
        'created_at' => 'datetime',
        'updated_at' => 'datetime'
    ];
    
    /**
     * Retorna a URL completa da foto
     */
    public function getPhotoUrlAttribute()
    {
        if (!$this->photo_path) {
            return null;
        }
        
        return asset('storage/' . $this->photo_path);
    }
}

/*
Exemplo de resposta JSON que a API Laravel deve retornar:

GET /api/employee/123/photo
Authorization: Bearer seu-token-aqui

Resposta de Sucesso (200):
{
    "success": true,
    "employee_id": "123",
    "employee_name": "João Silva", 
    "photo_url": "https://meusite-laravel.com.br/storage/employees/123.jpg",
    "photo_size": 245760,
    "updated_at": "2024-01-15T10:30:00.000000Z"
}

Resposta de Erro - Funcionário não encontrado (404):
{
    "error": "Funcionário não encontrado",
    "employee_id": "123"
}

Resposta de Erro - Sem foto (404):
{
    "error": "Funcionário não possui foto cadastrada", 
    "employee_id": "123"
}

Resposta de Erro - Não autorizado (401):
{
    "error": "Unauthorized"
}
*/
?>