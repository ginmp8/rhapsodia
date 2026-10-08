# Optional PowerShell adapter. Does not change execution policy or install tools.
$ErrorActionPreference = 'Stop'
$RuntimeArgs = $args
$Probe = 'import json,sys; sys.exit(2) if sys.version_info < (3,10) else print(json.dumps(sys.executable))'
$Candidates = @()
if ($env:RHAPSODIA_PYTHON) {
    if (-not [System.IO.File]::Exists($env:RHAPSODIA_PYTHON)) {
        throw 'RHAPSODIA_PYTHON must name a trusted executable file.'
    }
    $Candidates = @($env:RHAPSODIA_PYTHON)
} else {
    foreach ($Name in @('python3', 'python')) {
        $Found = Get-Command $Name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        # Do not open a Windows Store execution alias during discovery.
        if ($Found -and $Found.Source -notmatch '[\\/]WindowsApps[\\/]') {
            $Candidates += $Found.Source
        }
    }
}
$PythonPath = $null
foreach ($Candidate in ($Candidates | Select-Object -Unique)) {
    try {
        $Output = & $Candidate -I -S -c $Probe 2>$null
        if ($LASTEXITCODE -eq 0) {
            $Resolved = $Output | ConvertFrom-Json
            if ([System.IO.Path]::IsPathRooted($Resolved) -and [System.IO.File]::Exists($Resolved)) {
                $PythonPath = $Resolved
                break
            }
        }
    } catch {
        if ($env:RHAPSODIA_PYTHON) { throw }
    }
}
if (-not $PythonPath) {
    throw 'Python 3.10+ unavailable. Set RHAPSODIA_PYTHON to a trusted interpreter. Nothing was installed.'
}
& $PythonPath -I -S -B (Join-Path $PSScriptRoot 'runtime.py') @RuntimeArgs
exit $LASTEXITCODE
