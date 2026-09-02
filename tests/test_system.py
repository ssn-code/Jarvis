from backend.system.monitor import get_system_status
from backend.core.models import SystemStatus


def test_system_status_metrics():
    """Verify that get_system_status collects real system metrics."""
    status = get_system_status()
    assert isinstance(status, SystemStatus)
    assert status.cpu_percent >= 0.0
    assert status.memory_total_mb > 0
    assert status.memory_percent >= 0.0
    assert status.disk_total_gb > 0
    assert status.os != ""
    assert status.uptime_seconds >= 0.0
