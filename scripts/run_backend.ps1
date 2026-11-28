param([switch]$ManagedDesktop)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$pythonExe = "C:\PythonEnvs\connlab\.venv\Scripts\python.exe"
$port = 8000

if (-not $ManagedDesktop -and -not (Test-Path -LiteralPath $pythonExe -PathType Leaf)) {
    throw "ConnLab Python environment not found: $pythonExe"
}

$mutex = [Threading.Mutex]::new($false, "Global\ConnLab.Development.Backend.127.0.0.1.$port")
$owned = $false
try {
    try {
        $owned = $mutex.WaitOne(0)
    } catch [Threading.AbandonedMutexException] {
        # Windows grants ownership to this process when the previous owner exited.
        $owned = $true
    }
    if (-not $owned) {
        throw "The ConnLab development backend is already starting or running on port $port. Use the existing session."
    }

    # An older launcher or another application may listen without taking our mutex.
    $listener = [Net.Sockets.TcpListener]::new([Net.IPAddress]::Loopback, $port)
    try {
        $listener.ExclusiveAddressUse = $true
        $listener.Start()
    } catch [Net.Sockets.SocketException] {
        throw "Cannot start the development backend on 127.0.0.1:$port. Check which application is using this port. $($_.Exception.Message)"
    } finally {
        $listener.Stop()
    }

    Set-Location -LiteralPath $repoRoot
    if ($ManagedDesktop) {
        # Keep ownership through the shell lifecycle, including its backend readiness check.
        & py -m backend.desktop.managed_development_launcher
    } else {
        Write-Host "Starting ConnLab development backend at http://127.0.0.1:$port"
        & $pythonExe -m uvicorn backend.api.development:create_app --factory --host 127.0.0.1 --port $port --reload --reload-dir (Join-Path $repoRoot "backend")
    }
} finally {
    if ($owned) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
exit $LASTEXITCODE
