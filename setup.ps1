. "$PSScriptRoot\lang.ps1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir
$needRestart = $false
$sep = "============================================"

Write-Host $sep -ForegroundColor Cyan
Write-Host (T 'setup_title') -ForegroundColor Cyan
Write-Host $sep -ForegroundColor Cyan
Write-Host ""

# ---- Python ----
Write-Host (T 'setup_py_check') -ForegroundColor Yellow
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host (T 'setup_py_not') -ForegroundColor Yellow
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) {
        Write-Host (T 'setup_py_fail') -ForegroundColor Red
        Read-Host (T 'run_press_enter')
        exit 1
    }
    Write-Host (T 'setup_py_inst') -ForegroundColor Green
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}
Write-Host (T 'setup_py_ok') -ForegroundColor Green

# ---- Dependencies ----
Write-Host ""
Write-Host (T 'setup_dep') -ForegroundColor Yellow
pip install -r requirements.txt -q
if ($LASTEXITCODE -ne 0) {
    Write-Host (T 'setup_dep_fail') -ForegroundColor Red
    Read-Host (T 'run_press_enter')
    exit 1
}
Write-Host (T 'setup_done') -ForegroundColor Green

# ---- ffmpeg ----
Write-Host ""
Write-Host (T 'setup_ff_check') -ForegroundColor Yellow
$ffmpeg = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ffmpeg) {
    Write-Host (T 'setup_ff_not') -ForegroundColor Yellow
    winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    $needRestart = $true
    Write-Host (T 'setup_done') -ForegroundColor Green
} else {
    Write-Host ((T 'setup_ff_found') + $ffmpeg.Source) -ForegroundColor Green
}

# ---- config.py ----
Write-Host ""
Write-Host (T 'setup_cfg_check') -ForegroundColor Yellow
if (-not (Test-Path "config.py")) {
    $cfg = "# Video Analysis Config`nDEEPSEEK_API_KEY = `"your-api-key-here`"`nFFMPEG_BIN_DIR = `"`"`nWHISPER_MODEL = `"tiny`"`n"
    $cfg | Out-File -FilePath "config.py" -Encoding UTF8
    Write-Host (T 'setup_cfg_new') -ForegroundColor Green
} else {
    Write-Host (T 'setup_cfg_exist') -ForegroundColor Green
}

# ---- Complete ----
Write-Host ""
Write-Host $sep -ForegroundColor Cyan
Write-Host (T 'setup_complete') -ForegroundColor Cyan
if ($needRestart) { Write-Host (T 'setup_restart') -ForegroundColor Yellow }
Write-Host (T 'setup_step1') -ForegroundColor White
Write-Host (T 'setup_step2') -ForegroundColor White
Write-Host (T 'setup_step3') -ForegroundColor White
Write-Host $sep -ForegroundColor Cyan
Read-Host (T 'run_press_enter')
