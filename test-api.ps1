# Teste da API /api/compare
$headers = @{
    'Content-Type' = 'application/json'
}

$body = @'
{
    "reference_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABmJLR0QA/wD/AP+gvaeTAAAA+UlEQVQ4y+3UMUoDQRTG8Z8psJBUKTyAR7ATvIBgKTYW1oKtnRewsbK0sbKQNF7BQkQh2FhYiI2FEAKvMAvDMruzG7Dxw8DweG/+7817M/znVdE+1zjgGZ94wQ1GcY4Z9GXgCQ5wj3XcYh3X+MIR9rGZgQd4xQZucI5LbOIKnzjFXgYe4x0HuMtiF7jAYwbu4hW7eMhi57jEUwbu4AU7eM5iZ7jCcwb+xTO28ZLFznCNlwz8iyds4SmLneIGrxn4F4/YxEMWO8Et3jLwLx6wgfssto87vGfgX9xjHXdZbA93+MjAv7jDGm6z2C5u8ZmBf3GLVdxksR3c4CsD/+IGK7jOYlu4xncG/sU1lnGVxTZxhe8M/IsrLOEyi23gEj8Z+BcXWMQFFlvHOf4D2p9jQqR/0YAAAAAASUVORK5CYII=",
    "captured_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABQAAAAUCAYAAACNiR0NAAAABmJLR0QA/wD/AP+gvaeTAAAA+UlEQVQ4y+3UMUoDQRTG8Z8psJBUKTyAR7ATvIBgKTYW1oKtnRewsbK0sbKQNF7BQkQh2FhYiI2FEAKvMAvDMruzG7Dxw8DweG/+7817M/znVdE+1zjgGZ94wQ1GcY4Z9GXgCQ5wj3XcYh3X+MIR9rGZgQd4xQZucI5LbOIKnzjFXgYe4x0HuMtiF7jAYwbu4hW7eMhi57jEUwbu4AU7eM5iZ7jCcwb+xTO28ZLFznCNlwz8iyds4SmLneIGrxn4F4/YxEMWO8Et3jLwLx6wgfssto87vGfgX9xjHXdZbA93+MjAv7jDGm6z2C5u8ZmBf3GLVdxksR3c4CsD/+IGK7jOYlu4xncG/sU1lnGVxTZxhe8M/IsrLOEyi23gEj8Z+BcXWMQFFlvHOf4D2p9jQqR/0YAAAAAASUVORK5CYII=",
    "employee_id": "123"
}
'@

try {
    Write-Host "Testando API na porta 8000..."
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/compare" -Method POST -Headers $headers -Body $body
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Erro ao conectar na porta 8000: $($_.Exception.Message)"
    Write-Host "Detalhes: $($_.ErrorDetails.Message)"
}

Write-Host "`n--- Testando via Nginx na porta 80 ---"
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1/api/compare" -Method POST -Headers $headers -Body $body
    Write-Host "Status Code: $($response.StatusCode)"
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "Erro ao conectar via Nginx: $($_.Exception.Message)"
    Write-Host "Detalhes: $($_.ErrorDetails.Message)"
}