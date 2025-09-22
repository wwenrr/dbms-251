$venvPython = ".\venv\Scripts\python.exe"

if (-not (Test-Path $venvPython)) {
    Write-Error "Virtual environment not found. Please run install.ps1 first."
    exit 1
}

# Chạy file với pdb (Python debugger)
& $venvPython -m pdb "src/run.py" @args
