# ConnLab Phase 7 冒烟测试 - 快速启动脚本
# 此脚本帮助你快速开始测试

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "ConnLab Phase 7 冒烟测试 - 快速启动" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# 检查是否在正确的目录
$currentDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not (Test-Path (Join-Path $currentDir "SMOKE_TEST_GUIDE.md"))) {
    Write-Host "❌ 错误: 请在 test_by_third 目录中运行此脚本" -ForegroundColor Red
    exit 1
}

Write-Host "📚 可用资源:" -ForegroundColor Green
Write-Host "  1. README.md - 快速开始指南" -ForegroundColor White
Write-Host "  2. SMOKE_TEST_GUIDE.md - 完整测试指南（13 个测试）" -ForegroundColor White
Write-Host "  3. TEST_DATA_PREPARATION.md - 测试数据准备指南" -ForegroundColor White
Write-Host "  4. run_all_smoke_tests.ps1 - 一键自动化测试" -ForegroundColor White
Write-Host "  5. verify_*.py - Python 验证脚本" -ForegroundColor White
Write-Host ""

Write-Host "🚀 快速开始选项:" -ForegroundColor Green
Write-Host ""
Write-Host "  [1] 阅读快速开始指南 (README.md)" -ForegroundColor Yellow
Write-Host "  [2] 查看完整测试指南 (SMOKE_TEST_GUIDE.md)" -ForegroundColor Yellow
Write-Host "  [3] 了解如何准备测试数据" -ForegroundColor Yellow
Write-Host "  [4] 运行自动化测试（需要后端运行）" -ForegroundColor Yellow
Write-Host "  [5] 查看实现总结" -ForegroundColor Yellow
Write-Host "  [0] 退出" -ForegroundColor Yellow
Write-Host ""

$choice = Read-Host "请选择 (0-5)"

switch ($choice) {
    "1" {
        Write-Host "`n打开 README.md..." -ForegroundColor Cyan
        if (Get-Command "code" -ErrorAction SilentlyContinue) {
            code README.md
        } else {
            notepad README.md
        }
    }
    "2" {
        Write-Host "`n打开 SMOKE_TEST_GUIDE.md..." -ForegroundColor Cyan
        if (Get-Command "code" -ErrorAction SilentlyContinue) {
            code SMOKE_TEST_GUIDE.md
        } else {
            notepad SMOKE_TEST_GUIDE.md
        }
    }
    "3" {
        Write-Host "`n打开 TEST_DATA_PREPARATION.md..." -ForegroundColor Cyan
        if (Get-Command "code" -ErrorAction SilentlyContinue) {
            code TEST_DATA_PREPARATION.md
        } else {
            notepad TEST_DATA_PREPARATION.md
        }
    }
    "4" {
        Write-Host "`n检查后端服务..." -ForegroundColor Cyan
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -Method GET -TimeoutSec 3 -UseBasicParsing
            Write-Host "✅ 后端服务正在运行" -ForegroundColor Green
            Write-Host "`n开始自动化测试...`n" -ForegroundColor Cyan
            .\run_all_smoke_tests.ps1
        } catch {
            Write-Host "❌ 后端服务未运行" -ForegroundColor Red
            Write-Host ""
            Write-Host "请先运行以下命令启动后端:" -ForegroundColor Yellow
            Write-Host "  cd .." -ForegroundColor White
            Write-Host "  .\scripts\run_backend.ps1" -ForegroundColor White
            Write-Host ""
            $startBackend = Read-Host "是否现在启动后端? (y/n)"
            if ($startBackend -eq "y" -or $startBackend -eq "Y") {
                Set-Location ..
                .\scripts\run_backend.ps1
            }
        }
    }
    "5" {
        Write-Host "`n打开 IMPLEMENTATION_SUMMARY.md..." -ForegroundColor Cyan
        if (Get-Command "code" -ErrorAction SilentlyContinue) {
            code IMPLEMENTATION_SUMMARY.md
        } else {
            notepad IMPLEMENTATION_SUMMARY.md
        }
    }
    "0" {
        Write-Host "`n再见！👋`n" -ForegroundColor Cyan
        exit 0
    }
    default {
        Write-Host "`n❌ 无效选择" -ForegroundColor Red
    }
}

Write-Host "`n提示: 你也可以直接双击 .ps1 或 .py 文件运行特定脚本`n" -ForegroundColor Gray
