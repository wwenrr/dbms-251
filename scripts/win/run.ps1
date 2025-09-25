# run.ps1
$venvPython = ".\venv\Scripts\python.exe"

$versionOutput = & $venvPython --version
if ($versionOutput -notmatch "Python 3\.13\.7") {
    Write-Error "Incorrect Python version. Expected Python 3.13.7, but got: $versionOutput"
    exit 1
}

if (-not (Test-Path $venvPython)) {
    Write-Warning "Virtual environment not found. Please run install.ps1 first."
}

& $venvPython -B "src/run.py" @args
