param(
    [string]$lib
)

$venvPath = Resolve-Path "./venv"
$pythonExe = Join-Path $venvPath "Scripts/python.exe"
$pipExe    = Join-Path $venvPath "Scripts/pip.exe"

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

try {
    python -m venv --help > $null 2>&1
} catch {
    Write-Host "venv not found, installing..."
    python -m pip install --upgrade pip
    python -m pip install virtualenv
}

if (-not (Test-Path $venvPath)) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

& $pythonExe -m pip install --upgrade pip

if ($lib) {
    Write-Host "Installing library: $lib"
    & $pipExe install $lib

    & $pipExe freeze | Out-File -Encoding utf8 "req.txt"
} else {
    if (-not (Test-Path "req.txt")) {
        Write-Host "req.txt not found. Creating empty req.txt..."
        New-Item -ItemType File -Path "req.txt" -Force | Out-Null
    }

    Write-Host "Installing from req.txt..."
    & $pipExe install -r req.txt
}
