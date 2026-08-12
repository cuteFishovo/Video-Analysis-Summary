# Language Module - reads lang.json
# Keys: 1=English 2=Chinese 3=Japanese 4=Korean 5=Spanish 6=French

$langFile = "$PSScriptRoot\lang.txt"

# Auto-create lang.txt (default: English)
if (-not (Test-Path $langFile)) {
    "1" | Out-File -FilePath $langFile -Encoding UTF8 -NoNewline
    $langKey = "1"
} else {
    $raw = (Get-Content $langFile -Raw).Trim()
    if ($raw -match '^[1-6]$') {
        $langKey = $raw
    } else {
        "1" | Out-File -FilePath $langFile -Encoding UTF8 -NoNewline
        $langKey = "1"
    }
}

$global:langIdx  = [int]$langKey - 1
$global:langKey  = $langKey
$env:VIDEO_ANALYSIS_LANG = $langKey

# Load translations from JSON
$jsonPath = "$PSScriptRoot\lang.json"
if (Test-Path $jsonPath) {
    $data = Get-Content $jsonPath -Raw -Encoding UTF8 | ConvertFrom-Json
    # Flatten nested JSON into a single hashtable: "section_key" -> array
    $flat = @{}
    foreach ($section in $data.PSObject.Properties) {
        foreach ($key in $section.Value.PSObject.Properties) {
            $flat["$($section.Name)_$($key.Name)"] = @($key.Value)
        }
    }
    $global:T = $flat
} else {
    Write-Host "ERROR: lang.json not found!" -ForegroundColor Red
    $global:T = @{}
}

function T($k) { return $global:T[$k][$global:langIdx] }
