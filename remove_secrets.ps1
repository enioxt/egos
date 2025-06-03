# Script para remover chaves de API de arquivos de histórico
# Alinhado com EGOS_PRINCIPLE:Data_Security

$files = @(
    "docs\core_materials\historical_changelogs\Updates system EVA.txt",
    "docs\core_materials\historical_changelogs\eva atendimento inicio.txt"
)

foreach ($file in $files) {
    $fullPath = Join-Path $PSScriptRoot $file
    
    if (Test-Path $fullPath) {
        Write-Host "Processando arquivo: $file"
        
        # Ler conteúdo
        $content = Get-Content $fullPath -Raw -Encoding UTF8
        
        # Substituir chaves de API por placeholder
        # Padrão para chaves da OpenAI: sk-XXXXXXXXXXXXXXXXXXXXXXXX
        $newContent = $content -replace 'sk-[A-Za-z0-9]{32,}', '[API_KEY_REDACTED]'
        
        # Salvar conteúdo modificado
        $newContent | Set-Content $fullPath -Encoding UTF8
        
        Write-Host "Chaves de API removidas de: $file"
    } else {
        Write-Host "Arquivo não encontrado: $file"
    }
}

Write-Host "Processo concluído. Por favor, verifique os arquivos modificados."
