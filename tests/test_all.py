import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import time


def test_hardware_database():
    print("[1/6] Testing HardwareDatabase...")
    from modules.hardware_database import HardwareDatabase
    hw = HardwareDatabase()
    cpu = hw.find_cpu("Ryzen 5 5500")
    gpu = hw.find_gpu("RTX 2060 Gaming Z")
    assert cpu is not None, "CPU not found"
    assert gpu is not None, "GPU not found"
    print(f"  CPU: {cpu['model']} ({len(cpu)} fields)")
    print(f"  GPU: {gpu['model']} ({len(gpu)} fields)")
    print(f"  DB has {len(hw.get_all_cpus())} CPUs, {len(hw.get_all_gpus())} GPUs")
    
    cpu_info = hw.get_cpu_temps("Ryzen 5 5500")
    gpu_info = hw.get_gpu_temps("RTX 2060 Gaming Z")
    assert cpu_info is not None
    assert gpu_info is not None
    print(f"  CPU temps: idle {cpu_info['idle_min']}-{cpu_info['idle_max']}C, load {cpu_info['load_min']}-{cpu_info['load_max']}C")
    print(f"  GPU hotspot warning: {gpu_info['hotspot_warning']}C, critical: {gpu_info['hotspot_critical']}C")
    return hw


def test_ai_engine(hw):
    print("[2/6] Testing AIEngine...")
    from modules.ai_engine import AIEngine
    ai = AIEngine(hardware_db=hw)
    ai.set_hardware_info("AMD Ryzen 5 5500", "NVIDIA GeForce RTX 2060 Gaming Z", "16 GB")
    print("  AI Engine initialized")
    
    sensor_data = {
        "cpu_temp": 75.0, "cpu_usage": 50.0, "gpu_temp": 70.0,
        "gpu_hotspot_temp": 92.0, "gpu_vram_temp": 85.0, "gpu_usage": 60.0,
        "gpu_fan_rpm": 1800.0, "gpu_fan_percent": 75.0, "gpu_power": 130.0,
        "ram_percent": 60.0, "ram_used": 9.0, "ram_total": 16.0,
        "disk_usage_percent": 50.0, "ssd_temp": 38.0
    }
    
    results = ai.analyze(sensor_data)
    print(f"  Normal analysis: {len(results)} results")
    for r in results:
        print(f"    [{r.severity}] {r.component}: {r.summary[:60]}")
    
    # Test critical values
    sensor_data["gpu_hotspot_temp"] = 106.0
    sensor_data["gpu_temp"] = 83.0
    results2 = ai.analyze(sensor_data)
    print(f"  Critical analysis: {len(results2)} results")
    has_danger = any(r.severity == "danger" for r in results2)
    assert has_danger, "Should have danger severity"
    print("  Critical detection works!")
    
    # Test thermal trend
    for i in range(15):
        fake_time = time.time() - (200 * 24 * 3600) - i * 3600
        ai.add_sensor_data({
            "timestamp": fake_time,
            "gpu_temp": 55.0 + i * 0.5,
            "cpu_temp": 50.0 + i * 0.3
        })
    
    sensor_data["gpu_hotspot_temp"] = 85.0
    sensor_data["gpu_temp"] = 68.0
    trend_results = ai.analyze(sensor_data)
    trend_found = any("Termal Trend" in r.component for r in trend_results)
    print(f"  Thermal trend analysis: {'found' if trend_found else 'not found'}")
    
    return ai


def test_web_researcher():
    print("[3/6] Testing WebResearcher...")
    from modules.web_researcher import WebResearcher
    wr = WebResearcher(enabled=False)
    assert wr.enabled == False
    print(f"  Web Researcher loaded (enabled: {wr.enabled})")
    wr.set_enabled(True)
    assert wr.enabled == True
    print("  Toggle on/off works")
    return wr


def test_database():
    print("[4/6] Testing Database...")
    from modules.database import Database
    import tempfile
    db_path = os.path.join(tempfile.gettempdir(), "test_hardware_assistant.db")
    db = Database(db_path)
    
    db.save_system_info("cpu_name", "Test CPU")
    db.save_sensor_data({
        "timestamp": time.time(), "cpu_temp": 45.0, "cpu_usage": 20.0,
        "gpu_temp": 50.0, "gpu_hotspot_temp": 65.0, "gpu_usage": 30.0,
        "ram_percent": 40.0, "disk_usage_percent": 35.0, "gpu_power": 80.0,
        "cpu_power": 40.0, "gpu_fan_rpm": 1200.0, "gpu_vram_temp": 60.0,
        "ssd_temp": 30.0
    })
    
    info = db.get_system_info("cpu_name")
    assert info == "Test CPU", f"Expected 'Test CPU', got '{info}'"
    
    recent = db.get_recent_sensor_data(minutes=5)
    assert len(recent) > 0, "Should have sensor data"
    
    db.save_analysis({
        "timestamp": time.time(), "component": "CPU",
        "status": "warning", "severity": "warning",
        "summary": "Test analysis", "details": "Testing",
        "suggestions": ["Suggestion 1"]
    })
    
    db.save_chat_message("user", "Test message")
    chat = db.get_chat_history()
    assert len(chat) > 0
    
    db.cleanup_old_data(retention_days=365)
    stats = db.get_statistics(days=30)
    assert "total_records" in stats
    
    db.close()
    os.remove(db_path)
    print("  All database operations passed")
    return db


def test_notification_manager():
    print("[5/6] Testing NotificationManager...")
    from modules.notification_manager import NotificationManager
    nm = NotificationManager()
    
    nm.notify("Test Info", "This is a test", "info", "CPU")
    nm.notify("Test Warning", "High temperature detected", "warning", "GPU")
    nm.notify("Test Danger", "Critical temperature!", "danger", "GPU")
    
    all_notifs = nm.get_notifications()
    unread = nm.get_unread_count()
    print(f"  Notifications: {len(all_notifs)}, unread: {unread}")
    assert len(all_notifs) == 3
    assert unread == 3
    
    nm.mark_all_read()
    assert nm.get_unread_count() == 0
    print("  Mark all read works")
    
    nm.notify("New Alert", "Something happened", "warning", "CPU")
    recent = nm.get_recent(limit=2)
    print(f"  Recent notifications: {len(recent)}")
    
    nm.dismiss(recent[0].id)
    remaining = nm.get_notifications()
    print(f"  After dismiss: {len(remaining)} visible")
    
    nm.clear_all()
    assert len(nm.get_notifications()) == 0
    print("  Clear all works")


def test_sensor_manager():
    print("[6/6] Testing SensorManager...")
    from modules.sensor_manager import SensorManager
    sm = SensorManager(update_interval=0.5)
    
    data = sm.read_once()
    print(f"  CPU usage: {data.cpu_usage:.1f}%")
    print(f"  RAM: {data.ram_percent:.1f}%")
    print(f"  Uptime: {sm.get_formatted_uptime()}")
    print(f"  CPU Name: {sm.get_cpu_name()[:30]}")
    print(f"  Windows: {sm.get_windows_version()[:30]}")
    
    system_info = sm.get_system_info()
    assert isinstance(system_info, dict), "system_info should be a dict"
    
    sm.start()
    callback_data = []
    def cb(d):
        callback_data.append(d)
    sm.add_callback(cb)
    time.sleep(1.5)
    sm.stop()
    print(f"  Callbacks received: {len(callback_data)}")
    print("  SensorManager works correctly!")


if __name__ == "__main__":
    print("=" * 60)
    print("  ThermixAI - Test Suite")
    print("=" * 60)
    print()
    
    hw = test_hardware_database()
    print()
    ai = test_ai_engine(hw)
    print()
    test_web_researcher()
    print()
    test_database()
    print()
    test_notification_manager()
    print()
    test_sensor_manager()
    
    print()
    print("=" * 60)
    print("  TUM TESTLER BASARIYLA GECTI")
    print("=" * 60)
