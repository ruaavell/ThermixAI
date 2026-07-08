<#
.SYNOPSIS
    Elevated LibreHardwareMonitor sensor reader.
    Launches with admin rights (UAC prompt) and continuously reads all hardware sensors,
    writing results to a temp JSON file for the parent app to consume.
#>

param(
    [string]$DllPath = "",
    [string]$OutputFile = ""
)

if (-not $DllPath) {
    $DllPath = Join-Path $PSScriptRoot "LibreHardwareMonitorLib.dll"
}
if (-not (Test-Path $DllPath)) {
    Write-Error "DLL not found: $DllPath"
    exit 1
}
if (-not $OutputFile) {
    $OutputFile = Join-Path $env:TEMP "lhm_sensors.json"
}

try {
    [System.Reflection.Assembly]::LoadFrom($DllPath) | Out-Null
} catch {
    Write-Error "Failed to load DLL: $_"
    exit 1
}

$computer = New-Object LibreHardwareMonitor.Hardware.Computer
$computer.IsCpuEnabled = $true
$computer.IsGpuEnabled = $true
$computer.IsMemoryEnabled = $true
$computer.IsMotherboardEnabled = $true
$computer.IsControllerEnabled = $true
$computer.IsStorageEnabled = $true
$computer.IsNetworkEnabled = $true
$computer.IsPsuEnabled = $true

try {
    $computer.Open()
} catch {
    Write-Error "Failed to open Computer: $_"
    exit 1
}

Write-Output "LHM Elevated Reader started. PID: $pid"
Write-Output "Output: $OutputFile"

# Signal that we're ready
$readyFile = $OutputFile -replace '\.json$', '.ready'
[System.IO.File]::WriteAllText($readyFile, $pid.ToString())

$lastWrite = 0
while ($true) {
    Start-Sleep -Milliseconds 1200
    $sensors = @{}
    try {
        foreach ($hw in $computer.Hardware) {
            $hw.Update()
            $ht = $hw.HardwareType.ToString()
            $hn = $hw.Name
            foreach ($s in $hw.Sensors) {
                $v = $s.Value
                if ($v -ne $null) {
                    $key = "$ht|$hn|$($s.SensorType.ToString())|$($s.Name)"
                    $sensors[$key] = [double]$v
                }
            }
            foreach ($sub in $hw.SubHardware) {
                $sub.Update()
                foreach ($s in $sub.Sensors) {
                    $v = $s.Value
                    if ($v -ne $null) {
                        $key = "$ht|$hn > $($sub.Name)|$($s.SensorType.ToString())|$($s.Name)"
                        $sensors[$key] = [double]$v
                    }
                }
            }
        }
        # Write to temp file
        $items = @()
        foreach ($kv in $sensors.GetEnumerator()) {
            $items += @{k=$kv.Key; v=$kv.Value}
        }
        $json = ConvertTo-Json @{sensors=$items; timestamp=(Get-Date -UFormat %s)} -Compress
        [System.IO.File]::WriteAllText($OutputFile, $json)
        
        # Update ready file timestamp to show we're alive
        [System.IO.File]::WriteAllText($readyFile, $pid.ToString())
    } catch {
        # Silently continue on read errors
    }
}
