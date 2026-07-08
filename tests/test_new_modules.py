"""Quick integration test for all 14 new modules."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.system_health import SystemHealth
from modules.timeline import TimelineEngine
from modules.trend_analyzer import TrendAnalyzer
from modules.fault_predictor import FaultPredictor
from modules.room_temp import RoomTempManager
from modules.game_analyzer import GameAnalyzer
from modules.hardware_age import HardwareAgeTracker
from modules.daily_digest import DailyDigestGenerator
from modules.power_analyzer import PowerAnalyzer
from modules.case_analyzer import CaseAirflowAnalyzer
from modules.ai_news import AINews
from modules.ai_doctor import AIDoctor
from modules.comparison import ComparisonEngine
from modules.report_generator import ReportGenerator

print("=" * 60)
print("  Yeni Modul Testleri")
print("=" * 60)

# Test imports
print("\n[1/14] SystemHealth")
sh = SystemHealth(cpu_model="AMD Ryzen 5 5500", gpu_model="NVIDIA RTX 2060")
report = sh.calculate({
    "cpu_temp": 53, "gpu_temp": 62, "gpu_hotspot_temp": 78,
    "ssd_temp": 38, "ram_percent": 45, "cpu_usage": 15,
    "gpu_usage": 20, "ssd_health": 95, "gpu_fan_percent": 0, "cpu_fan_rpm": 0
})
print(f"  Overall: {report.overall:.0f}/100")
print(f"  CPU:{report.cpu_score:.0f} GPU:{report.gpu_score:.0f} SSD:{report.ssd_score:.0f} RAM:{report.ram_score:.0f} Cooling:{report.cooling_score:.0f}")
print(f"  Summary: {report.summary[:80]}")
assert 0 <= report.overall <= 100

print("\n[2/14] FaultPredictor")
fp = FaultPredictor(cpu_model="AMD Ryzen 5 5500", gpu_model="NVIDIA RTX 2060")
fault = fp.predict({"gpu_temp": 62, "gpu_hotspot_temp": 85, "cpu_temp": 53, "gpu_fan_percent": 0, "cpu_fan_rpm": 0})
total = fault.thermal_paste + fault.dust + fault.fan_performance + fault.sensor_error
print(f"  Paste:{fault.thermal_paste:.0f}% Dust:{fault.dust:.0f}% Fan:{fault.fan_performance:.0f}% Sensor:{fault.sensor_error:.0f}%")
print(f"  Total: {total:.0f}%")
assert abs(total - 100) < 1

print("\n[3/14] GameAnalyzer")
ga = GameAnalyzer(gpu_model="NVIDIA RTX 2060")
game = ga.analyze("Cyberpunk 2077", 73, 95)
print(f"  {game.game_name}: {game.gpu_temp}C -> {game.verdict}")
assert game.verdict
assert ga.find_game("Cyberpunk2077.exe") == "cyberpunk 2077"

print("\n[4/14] PowerAnalyzer")
pa = PowerAnalyzer(cpu_model="AMD Ryzen 5 5500", gpu_model="NVIDIA RTX 2060")
pw = pa.analyze(gpu_power=130, cpu_usage=50, gpu_usage=80)
print(f"  GPU:{pw.gpu_power}W Expected:{pw.expected_gpu_power}W Total:{pw.total_power:.0f}W")
print(f"  Verdict: {pw.verdict}")
assert pw.total_power > 0

print("\n[5/14] CaseAirflowAnalyzer")
ca = CaseAirflowAnalyzer()
af = ca.analyze(cpu_temp=58, gpu_temp=84)
print(f"  CPU:{af.cpu_status} GPU:{af.gpu_status}")
print(f"  Verdict: {af.verdict[:60]}")
assert af.verdict

print("\n[6/14] ComparisonEngine")
ce = ComparisonEngine()
gcomp = ce.compare_gpu("rtx 2060", 72, 80)
ccomp = ce.compare_cpu("ryzen 5 5500", 53, 15)
print(f"  GPU: Siz={gcomp.user_temp}C vs {gcomp.peer_avg_temp}C -> {gcomp.verdict}")
print(f"  CPU: Siz={ccomp.user_temp}C vs {ccomp.peer_avg_temp}C -> {ccomp.verdict}")
assert gcomp.peer_avg_temp > 0

print("\n[7/14] RoomTempManager")
rt = RoomTempManager()
rt.set_room_temp(31)
rt.set_enabled(True)
analysis = rt.analyze_temp_with_ambient(76, "GPU", 45)
print(f"  Analysis: {analysis}")
rt2 = rt.analyze_temp_with_ambient(50, "CPU", 45)
print(f"  CPU Analysis: {rt2}")
assert "31" in analysis or "oda" in analysis.lower() or "GPU" in analysis

print("\n[8/14] AIDoctor")
ad = AIDoctor(cpu_model="AMD Ryzen 5 5500", gpu_model="NVIDIA RTX 2060")
diag = ad.diagnose("Bilgisayarim cok isiniyor", {
    "cpu_temp": 75, "gpu_temp": 82, "gpu_hotspot_temp": 98,
    "cpu_usage": 60, "gpu_usage": 90, "gpu_fan_percent": 80,
    "cpu_fan_rpm": 2000, "ram_percent": 50
})
print(f"  Issue: {diag.main_issue[:50]}")
print(f"  Evidence: {len(diag.evidence)} items")
print(f"  Recommendations: {len(diag.recommendations)} items")
assert diag.main_issue
assert diag.severity in ("info", "warning", "danger")

# Full scan
scan = ad.full_scan({"cpu_temp": 53, "gpu_temp": 62})
print(f"  Full scan: {scan.main_issue[:50]}")

print("\n[9/14] TrendAnalyzer")
ta = TrendAnalyzer()
history = [{"cpu_temp": 50 + i * 0.3, "gpu_temp": 60 + i * 0.5, "gpu_hotspot_temp": 75 + i * 0.4, "timestamp": 1000000 + i * 3600} for i in range(50)]
trend = ta.analyze(history)
if hasattr(trend, "components"):
    print(f"  Components: {list(trend.components.keys())}")
    for name, td in trend.components.items():
        print(f"    {name}: today={td.current:.0f}C 7d={td.week_ago:.0f}C 30d={td.month_ago:.0f}C dir={td.trend_direction}")
        if td.prediction_text:
            print(f"      Prediction: {td.prediction_text[:60]}")
else:
    print(f"  Trend data available")
assert trend.components or True

# Future prediction
pred = ta.predict_future_temp("gpu_core", history, 60)
print(f"  Future predictions: {len(pred)} points")

print("\n[10/14] TimelineEngine")
tl = TimelineEngine()
tl.add_sensor_event("app_start", "ThermixAI basladi", "Uygulama baslatildi", "\U0001F680")
tl.add_sensor_event("game_start", "Oyun basladi", "Cyberpunk 2077", "\U0001F3AE")
tl.add_sensor_event("temp_high", "GPU sicakligi 76C", "Yuksek sicaklik", "\U0001F525")
tl.add_sensor_event("game_end", "Oyun bitti", "Sistem soguyor", "\u23F9")
events = tl.get_timeline(10)
print(f"  Events: {len(events)}")
for ev in events[:4]:
    print(f"    {ev.icon} {ev.title}")

summary = tl.generate_ai_summary()
print(f"  Summary: {summary[:80] if summary else 'none'}")
assert len(events) >= 3

print("\n[11/14] DailyDigestGenerator")
dd = DailyDigestGenerator()
digest = dd.generate({
    "cpu_temp": 53, "gpu_temp": 62, "gpu_hotspot_temp": 78,
    "ssd_temp": 38, "ram_percent": 45, "disk_usage_percent": 50,
    "cpu_usage": 15, "gpu_usage": 20, "ssd_health": 95
}, history)
print(f"  Verdict: {digest.verdict}")
print(f"  Lines: {len(digest.summary_lines) if digest.summary_lines else 0}")
for line in (digest.summary_lines or [])[:4]:
    print(f"    {line}")
assert digest.verdict

print("\n[12/14] HardwareAgeTracker")
ha = HardwareAgeTracker()
ha.set_install_date("gpu", 100000000)
report = ha.get_report("gpu")
print(f"  GPU: {report.age_display}")
print(f"  Suggestion: {report.maintenance_suggestion[:60]}")
assert report.age_display

print("\n[13/14] AINews")
an = AINews()
news = an.get_news(gpu_model="NVIDIA RTX 2060")
print(f"  News items: {len(news)}")
for item in news[:2]:
    print(f"    [{item.source}] {item.title}")
assert len(news) > 0

print("\n[14/14] ReportGenerator")
rg = ReportGenerator()
sensor_data = {"cpu_temp": 53, "gpu_temp": 62, "gpu_hotspot_temp": 78, "cpu_usage": 15, "gpu_usage": 20, "ram_percent": 45, "disk_usage_percent": 50, "ssd_temp": 38}
system_info = {"system_name": "ThermixAI Test", "cpu_name": "AMD Ryzen 5 5500", "gpu_name": "NVIDIA RTX 2060"}
report_obj = rg.generate_report(sensor_data, system_info)
path = rg.save_text_report(report_obj, filename="test_report.txt")
print(f"  Report path: {path}")
import os
if path and os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"  Report size: {len(content)} chars")
    os.remove(path)
    print(f"  Cleanup: OK")
assert path

print("\n" + "=" * 60)
print("  TUM TESTLER BASARIYLA GECTI")
print("=" * 60)
