import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

print("=== SENSOR DIAGNOSTIC ===\n")

# 1. Check sensor_manager
print("[1] SensorManager read_once:")
from modules.sensor_manager import SensorManager
sm = SensorManager()
data = sm.read_once()
print(f"  CPU: {data.cpu_temp:.1f}C, usage={data.cpu_usage:.1f}%, freq={data.cpu_freq:.0f}MHz")
print(f"  GPU: {data.gpu_temp:.1f}C, hotspot={data.gpu_hotspot_temp:.1f}C, usage={data.gpu_usage:.1f}%")
print(f"  GPU VRAM: {data.gpu_vram_used:.0f}/{data.gpu_vram_total:.0f}MB")
print(f"  GPU Fan: {data.gpu_fan_percent:.0f}%, power={data.gpu_power:.1f}W")
print(f"  RAM: %{data.ram_percent:.1f}")
print(f"  Disk: %{data.disk_usage_percent:.0f}")
print(f"  CPU name: {sm.get_cpu_name()}")
print(f"  GPU name: {sm.get_gpu_name()}")

# 2. Try various WMI temperature sources
print("\n[2] WMI Temperature Sources:")

import win32com.client

# LibreHardwareMonitor
try:
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\LibreHardwareMonitor")
    sensors = wmi.ExecQuery("SELECT * FROM Sensor WHERE SensorType='Temperature'")
    count = 0
    for s in sensors:
        print(f"  LibreHW: {s.Name} = {s.Value}C (Parent: {s.Parent})")
        count += 1
    if count == 0:
        print("  LibreHardwareMonitor: No sensors (not installed)")
except Exception as e:
    print(f"  LibreHardwareMonitor: {e}")

# OpenHardwareMonitor
try:
    wmi = win32com.client.GetObject("winmgmts:\\\\.\\root\\OpenHardwareMonitor")
    sensors = wmi.ExecQuery("SELECT * FROM Sensor WHERE SensorType='Temperature'")
    count = 0
    for s in sensors:
        print(f"  OpenHW: {s.Name} = {s.Value}C (Parent: {s.Parent})")
        count += 1
    if count == 0:
        print("  OpenHardwareMonitor: No sensors (not installed)")
except Exception as e:
    print(f"  OpenHardwareMonitor: {e}")

# Win32_TemperatureProbe
try:
    import wmi
    c = wmi.WMI()
    for probe in c.Win32_TemperatureProbe():
        print(f"  Win32_TemperatureProbe: {probe.Name} = {probe.CurrentReading}")
except Exception as e:
    print(f"  Win32_TemperatureProbe: {e}")

# 3. Try to use nvidia-smi more fields
print("\n[3] nvidia-smi extended info:")
import subprocess
try:
    result = subprocess.run(
        ["nvidia-smi", "--query-gpu=temperature.gpu,power.draw,fan.speed,clocks.current.graphics,clocks.current.memory,memory.used,memory.total,utilization.gpu,name", "--format=csv,noheader,nounits"],
        capture_output=True, text=True, timeout=5
    )
    print(f"  Output: {result.stdout.strip()}")
    if result.returncode != 0:
        print(f"  Stderr: {result.stderr}")
except Exception as e:
    print(f"  Error: {e}")

# 4. Check for alternative temp sources
print("\n[4] Alternative sources:")
# WMIC path
try:
    result = subprocess.run(["wmic", "/namespace:\\\\root\\wmi", "path", "MSAcpi_ThermalZoneTemperature", "get", "CurrentTemperature"], capture_output=True, text=True, timeout=10)
    print(f"  WMIC MSAcpi: {result.stdout.strip()[:100]} (rc={result.returncode})")
except Exception as e:
    print(f"  WMIC MSAcpi error: {e}")

# Check admin status
import ctypes
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
print(f"  Admin rights: {bool(is_admin)}")

print("\n=== DONE ===")
