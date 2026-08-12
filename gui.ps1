# ============================================
# Video Analysis Tool - Console Menu
# ============================================

. "$PSScriptRoot\lang.ps1"
$scriptDir = $PSScriptRoot

# ====== Language Switch Screen ======
function Switch-Language {
    Clear-Host
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host (T 'lang_title') -ForegroundColor Cyan
    Write-Host "============================================"
    Write-Host ""
    Write-Host (T 'lang_opt1') -ForegroundColor White
    Write-Host (T 'lang_opt2') -ForegroundColor White
    Write-Host (T 'lang_opt3') -ForegroundColor White
    Write-Host (T 'lang_opt4') -ForegroundColor White
    Write-Host (T 'lang_opt5') -ForegroundColor White
    Write-Host (T 'lang_opt6') -ForegroundColor White
    Write-Host ""
    $choice = Read-Host (T 'menu_prompt')
    if ($choice -match '^[1-6]$') {
        $choice | Out-File -FilePath "$scriptDir\lang.txt" -Encoding UTF8 -NoNewline
        $env:VIDEO_ANALYSIS_LANG = $choice
        Write-Host (T 'lang_saved') -ForegroundColor Green
    } else {
        Write-Host (T 'menu_invalid') -ForegroundColor Red
    }
    Start-Sleep -Milliseconds 1200
}

# ====== Main Menu Screen ======
function Show-Menu {
    Clear-Host
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host (T 'menu_title') -ForegroundColor Cyan
    Write-Host "============================================"
    Write-Host ""
    Write-Host (T 'menu_opt_setup') -ForegroundColor Yellow
    Write-Host (T 'menu_opt_run')   -ForegroundColor Yellow
    Write-Host (T 'menu_opt_lang')  -ForegroundColor Yellow
    Write-Host (T 'menu_opt_exit')  -ForegroundColor DarkGray
    Write-Host ""
}

# ====== Main Loop ======
do {
    Show-Menu
    $sel = Read-Host (T 'menu_prompt')

    switch ($sel) {
        '1' {
            Write-Host ""
            Write-Host (T 'status_running_setup') -ForegroundColor Yellow
            $proc = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoProfile -File `"$scriptDir\setup.ps1`"" -PassThru -Wait
            $msg = (T 'status_done_setup') + " $($proc.ExitCode)"
            $clr = if ($proc.ExitCode -eq 0) { 'Green' } else { 'Red' }
            Write-Host $msg -ForegroundColor $clr
            Read-Host ("`n" + (T 'run_press_enter'))
        }
        '2' {
            Write-Host ""
            Write-Host (T 'status_running_run') -ForegroundColor Yellow
            $proc = Start-Process powershell -ArgumentList "-ExecutionPolicy Bypass -NoProfile -File `"$scriptDir\run.ps1`"" -PassThru -Wait
            $msg = (T 'status_done_run') + " $($proc.ExitCode)"
            $clr = if ($proc.ExitCode -eq 0) { 'Green' } else { 'Red' }
            Write-Host $msg -ForegroundColor $clr
            Read-Host ("`n" + (T 'run_press_enter'))
        }
        '3' { Switch-Language }
        '0' { Write-Host (T 'status_bye') -ForegroundColor Cyan; break }
        default { Write-Host (T 'menu_invalid') -ForegroundColor Red; Start-Sleep -Milliseconds 800 }
    }
} while ($sel -ne '0')
