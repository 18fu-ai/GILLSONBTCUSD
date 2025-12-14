# backend/monitoring.py - PRODUCTION MONITORING
import psutil
import time
from datetime import datetime

class ProductionMonitor:
    """Production system monitoring"""

    def get_system_metrics(self):
        """Get comprehensive system metrics"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_usage": {
                "total": psutil.virtual_memory().total,
                "available": psutil.virtual_memory().available,
                "percent": psutil.virtual_memory().percent
            },
            "disk_usage": {
                "total": psutil.disk_usage('/').total,
                "used": psutil.disk_usage('/').used,
                "percent": psutil.disk_usage('/').percent
            },
            "network_io": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            },
            "system_uptime": time.time() - psutil.boot_time()
        }
