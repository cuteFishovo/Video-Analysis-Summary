. "$PSScriptRoot\lang.ps1"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host ""

# Find ffmpeg
$ffmpegFound = $false
$ffmpegDir = ""
$cmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
if ($cmd) {
    $ffmpegDir = Split-Path -Parent $cmd.Source
    $ffmpegFound = $true
}
if (-not $ffmpegFound) {
    $pkgDir = "$env:LOCALAPPDATA\Microsoft\WinGet\Packages"
    if (Test-Path $pkgDir) {
        $exe = Get-ChildItem -Path $pkgDir -Recurse -Filter "ffmpeg.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($exe) {
            $ffmpegDir = $exe.DirectoryName
            $ffmpegFound = $true
        }
    }
}
if (-not $ffmpegFound) {
    Write-Host (T 'run_ff_not') -ForegroundColor Red
    Read-Host (T 'run_press_enter')
    exit 1
}

$env:Path = "$ffmpegDir;$env:Path"
python run.py
Write-Host ""
Read-Host (T 'run_done_exit')
