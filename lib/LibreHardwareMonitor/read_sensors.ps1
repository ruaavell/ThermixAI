# Read sensors via LibreHardwareMonitorLib.dll directly (no GUI needed)
param([string]$DllPath = "")
if (-not $DllPath) { $DllPath = "$PSScriptRoot\LibreHardwareMonitorLib.dll" }
if (-not (Test-Path $DllPath)) { Write-Output '{}'; exit 1 }

try {
    [System.Reflection.Assembly]::LoadFrom($DllPath) | Out-Null
    $computer = New-Object LibreHardwareMonitor.Hardware.Computer
    $computer.IsCpuEnabled = $true
    $computer.IsGpuEnabled = $true
    $computer.IsMemoryEnabled = $true
    $computer.IsMotherboardEnabled = $true
    $computer.IsControllerEnabled = $true
    $computer.IsStorageEnabled = $true
    $computer.IsNetworkEnabled = $true
    $computer.Open()
    Start-Sleep -Milliseconds 600
    
    $r = @{}
    foreach ($hw in $computer.Hardware) {
        $hw.Update()
        $ht = $hw.HardwareType.ToString()
        $hn = $hw.Name
        foreach ($s in $hw.Sensors) {
            $v = $s.Value
            if ($v -ne $null) {
                $st = $s.SensorType.ToString()
                $sn = $s.Name
                $key = "$ht|$hn|$st|$sn"
                $r[$key] = [double]$v
            }
        }
        foreach ($sub in $hw.SubHardware) {
            $sub.Update()
            foreach ($s in $sub.Sensors) {
                $v = $s.Value
                if ($v -ne $null) {
                    $st = $s.SensorType.ToString()
                    $sn = $s.Name
                    $key = "$ht|$($hw.Name) > $($sub.Name)|$st|$sn"
                    $r[$key] = [double]$v
                }
            }
        }
    }
    $computer.Close()
    
    # Convert to flat JSON
    $items = @()
    foreach ($kv in $r.GetEnumerator()) { $items += @{k=$kv.Key; v=$kv.Value} }
    ConvertTo-Json @{sensors=$items} -Compress
}
catch { Write-Output '{}' }
