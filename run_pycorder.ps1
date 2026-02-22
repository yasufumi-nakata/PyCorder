param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$AppArgs
)

$ErrorActionPreference = "Stop"

$RootDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $RootDir

if (Get-Command py -ErrorAction SilentlyContinue) {
    $PythonCommand = "py"
    $PythonPrefix = @("-3")
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonCommand = "python3"
    $PythonPrefix = @()
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonCommand = "python"
    $PythonPrefix = @()
} else {
    throw "[error] Python interpreter not found (py/python3/python)."
}

function Invoke-HostPython {
    param([string[]]$Args)
    & $PythonCommand @PythonPrefix @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $PythonCommand $($PythonPrefix + $Args -join ' ')"
    }
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "[setup] Creating virtual environment at .venv"
    Invoke-HostPython @("-m", "venv", "--clear", ".venv")
}

$VenvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $VenvPython)) {
    throw "[error] Virtual environment is missing: $VenvPython"
}

$ProbeScript = @"
import importlib
for name in ("numpy", "scipy", "lxml", "PySide6", "pyqtgraph"):
    importlib.import_module(name)
"@

& $VenvPython "-c" $ProbeScript *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[setup] Installing dependencies from requirements.txt"
    & $VenvPython "-m" "pip" "install" "--upgrade" "pip" "setuptools" "wheel"
    if ($LASTEXITCODE -ne 0) { throw "pip bootstrap failed" }
    & $VenvPython "-m" "pip" "install" "-r" "requirements.txt"
    if ($LASTEXITCODE -ne 0) { throw "dependency installation failed" }
}

& $VenvPython "main.py" @AppArgs
exit $LASTEXITCODE
