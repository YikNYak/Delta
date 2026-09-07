# Delta installer - Made by okaydrku - only Delta.py needed, creates Delta folder + Delta.bat
# Run: powershell -ExecutionPolicy Bypass -File install.ps1
# Fresh PC: put Delta.py + install.ps1 in Downloads, run install.ps1 -> creates Downloads\Delta\Delta.bat
Write-Host "Delta installer - Made by okaydrku" -ForegroundColor Cyan

# Always use Downloads\Delta as target (so you only need to send Delta.py)
$downloads = Join-Path $env:USERPROFILE "Downloads"
$deltaRoot = Join-Path $downloads "Delta"
if (-not (Test-Path $deltaRoot)) {
    New-Item -ItemType Directory -Path $deltaRoot -Force | Out-Null
    Write-Host "[+] Created folder $deltaRoot" -ForegroundColor Green
} else {
    Write-Host "[+] Folder $deltaRoot exists" -ForegroundColor Gray
}

# If Delta.py is next to this script but not yet in Delta folder, copy it
$srcDelta = Join-Path $PSScriptRoot "Delta.py"
$dstDelta = Join-Path $deltaRoot "Delta.py"
if ((Test-Path $srcDelta) -and (-not (Test-Path $dstDelta) -or ( (Get-Item $srcDelta).Length -ne (Get-Item $dstDelta -ErrorAction SilentlyContinue).Length ))) {
    Copy-Item $srcDelta $dstDelta -Force
    Write-Host "[+] Copied Delta.py to $dstDelta" -ForegroundColor Green
}
# Also ensure install.ps1 is in Delta folder for later
$dstInstall = Join-Path $deltaRoot "install.ps1"
if ($PSScriptRoot -ne $deltaRoot -and (Test-Path $PSScriptRoot\install.ps1)) {
    Copy-Item "$PSScriptRoot\install.ps1" $dstInstall -Force -ErrorAction SilentlyContinue
}

# 1. Python check
function Test-Python {
    $c = Get-Command python -ErrorAction SilentlyContinue
    if (-not $c) { $c = Get-Command python3 -ErrorAction SilentlyContinue }
    if (-not $c) { $c = Get-Command py -ErrorAction SilentlyContinue }
    return $c
}
$py = Test-Python
if (-not $py) {
    Write-Host "[!] Python not found - trying winget..." -ForegroundColor Yellow
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    $installed = $false
    if ($winget) {
        try {
            winget install --id Python.Python.3.12 -e --accept-package-agreements --accept-source-agreements --silent --scope user
            Start-Sleep -Seconds 8
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $py = Test-Python
            if ($py) { $installed = $true; Write-Host "[+] Python installed via winget" -ForegroundColor Green }
        } catch { Write-Host "[!] winget failed" -ForegroundColor Yellow }
    }
    if (-not $installed) {
        Write-Host "[*] Downloading Python 3.12 installer..." -ForegroundColor Cyan
        $pyUrl = "https://www.python.org/ftp/python/3.12.7/python-3.12.7-amd64.exe"
        $pyExe = Join-Path $env:TEMP "python-installer.exe"
        try {
            Invoke-WebRequest -Uri $pyUrl -OutFile $pyExe -UseBasicParsing -TimeoutSec 120
            Start-Process -FilePath $pyExe -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_pip=1" -Wait
            Remove-Item $pyExe -Force -ErrorAction SilentlyContinue
            $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
            $py = Test-Python
            if ($py) { Write-Host "[+] Python installed" -ForegroundColor Green }
            else { Write-Host "[!] Python still not in PATH - restart PC and re-run" -ForegroundColor Red; pause; exit 1 }
        } catch {
            Write-Host "[!] Direct install failed - install manually from https://www.python.org/downloads/ (check Add to PATH)" -ForegroundColor Red
            pause; exit 1
        }
    }
} else {
    Write-Host "[+] Python found" -ForegroundColor Green
}

$pyCmd = "python"
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { $pyCmd = "py -3" }

# 2. Deps
Write-Host "[*] Installing requirements (rich pyfiglet requests)..." -ForegroundColor Cyan
Invoke-Expression "$pyCmd -m pip install --upgrade pip --quiet"
Invoke-Expression "$pyCmd -m pip install rich pyfiglet requests --quiet"
if ($LASTEXITCODE -ne 0) {
    Invoke-Expression "$pyCmd -m pip install --user rich pyfiglet requests"
}
Write-Host "[+] Requirements OK" -ForegroundColor Green

# 3. Delta.py check (already handled above)
if (Test-Path $dstDelta) { Write-Host "[+] Delta.py ready in $deltaRoot" -ForegroundColor Green }
else { Write-Host "[!] Delta.py missing - put Delta.py in $deltaRoot" -ForegroundColor Red }

# 3b. Unlocker (fixes fresh PC missing license / not appearing) like LuaTools Bst
Write-Host "[*] Checking Steam unlocker (BetterSteamTools)..." -ForegroundColor Cyan
Push-Location $deltaRoot
try {
    $unlockOut = & $pyCmd $dstDelta unlocker 2>&1 | Out-String
    Write-Host $unlockOut
    if ($unlockOut -match "Permission denied") {
        Write-Host "[!] Need admin for unlocker (Program Files) - right-click install.ps1 -> Run as administrator and retry" -ForegroundColor Yellow
    }
} catch {
    Write-Host "[!] Unlocker check failed" -ForegroundColor Yellow
}
Pop-Location

# 4. Create Delta.bat in Delta folder (so you only need to send Delta.py)
$bat = Join-Path $deltaRoot "Delta.bat"
$batContent = "@echo off`r`nchcp 65001 >nul`r`nset PYTHONIOENCODING=utf-8`r`nset PYTHONUTF8=1`r`npython -X utf8 `"%~dp0Delta.py`" %*`r`nif errorlevel 1 py -3 -X utf8 `"%~dp0Delta.py`" %*"
Set-Content -Path $bat -Value $batContent -Encoding ASCII
Write-Host "[+] Created $bat (you only need to send Delta.py, this is auto-created)" -ForegroundColor Green

# 5. Desktop shortcut removed per request

Write-Host ""
Write-Host "Done! Fresh PC ready:" -ForegroundColor Cyan
Write-Host "  Folder: $deltaRoot" -ForegroundColor White
Write-Host "  python Delta.py" -ForegroundColor White
Write-Host "  Only Delta.py needed - Delta.bat auto-created" -ForegroundColor Gray
Write-Host ""
pause
