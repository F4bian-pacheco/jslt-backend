# Script de utilidad para ejecutar tests
# Uso: .\run_tests.ps1 [opciones]

param(
    [switch]$Verbose,
    [switch]$Coverage,
    [switch]$Quick,
    [string]$File,
    [string]$Test
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "  JSLT Backend Test Runner" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Construir comando pytest
$cmd = "pytest"

if ($Quick) {
    $cmd += " --tb=no -q"
}
elseif ($Verbose) {
    $cmd += " -v"
}

if ($Coverage) {
    $cmd += " --cov=app --cov-report=html --cov-report=term"
    Write-Host "📊 Ejecutando con coverage..." -ForegroundColor Yellow
}

if ($File) {
    $cmd += " tests/$File"
    Write-Host "📁 Ejecutando archivo: $File" -ForegroundColor Yellow
}

if ($Test) {
    $cmd += "::$Test"
    Write-Host "🎯 Ejecutando test: $Test" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Comando: $cmd" -ForegroundColor Gray
Write-Host ""

# Ejecutar pytest
Invoke-Expression $cmd

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "  Test execution completed" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
