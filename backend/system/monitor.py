import platform
import time
import psutil
from backend.core.models import SystemStatus

START_TIME = time.time()


def get_system_status() -> SystemStatus:
    """Collects real-time system metrics (CPU, RAM, Disk, OS, Uptime)."""
    cpu_percent = psutil.cpu_percent(interval=None)

    mem = psutil.virtual_memory()
    memory_used_mb = round(mem.used / (1024 * 1024), 2)
    memory_total_mb = round(mem.total / (1024 * 1024), 2)
    memory_percent = mem.percent

    disk = psutil.disk_usage("/")
    disk_used_gb = round(disk.used / (1024 * 1024 * 1024), 2)
    disk_total_gb = round(disk.total / (1024 * 1024 * 1024), 2)
    disk_percent = disk.percent

    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
    uptime_seconds = round(time.time() - START_TIME, 2)

    return SystemStatus(
        cpu_percent=cpu_percent,
        memory_used_mb=memory_used_mb,
        memory_total_mb=memory_total_mb,
        memory_percent=memory_percent,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
        disk_percent=disk_percent,
        os=os_info,
        uptime_seconds=uptime_seconds,
    )
