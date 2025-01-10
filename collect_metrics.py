import time
import json
import redis
import psutil
from datetime import datetime

# 1. Initialize redis connection

# Adjust host/port/db/password based on your environment

r = redis.Redis(host="localhost", port=6379, db=0)

def collect_and_store_metrics():
    """
    Collects required metrics and stores them in Redis as a json string under the 'metrics' key
    """

    # 2. Gather metrics

    #------------------------------------------------------------------------------------------

    # A) Timestamp
    timestamp = str(datetime.now())

    # B) CPU frequency
    cpu_freq = psutil.cpu_freq().current #in MHZ

    # C) CPU frequency use per core
    cpu_percent_list = psutil.cpu_percent(interval=None, percpu=True)
    # We'll build a dict like {"cpu_percent-0": 10.5, "cpu_percent-1": 20.1, ...}

    # D) CPU stats
    cpu_stats = psutil.cpu_stats()
    ctx_switches = cpu_stats.ctx_switches
    interrupts = cpu_stats.interrupts
    soft_interrupts = cpu_stats.soft_interrupts
    syscalls = cpu_stats.syscalls

    # E) Virtual memory metrics
    vm = psutil.virtual_memory()
    vm_total = vm.total
    vm_available = vm.available
    vm_percent = vm.percent
    vm_used = vm.used
    vm_free = vm.free
    vm_active = vm.active
    vm_inactive = vm.inactive
    vm_buffers = getattr(vm, 'buffers', 0) # some OS may not have this
    vm_cached = getattr(vm, 'cached', 0) # likewise
    vm_shared = getattr(vm, 'shared', 0)
    vm_slab = getattr(vm, 'slab', 0)

    # F) Number of PIDs
    n_pids = len(psutil.pids())

    # G) Network metrics (example for interface 'eth0')
    #    Replace 'eth0' with the correct interface name on your system
    net_io = psutil.net_io_counters(pernic=True)
    eth_0_stats = net_io.get('eth0', None)
    if eth_0_stats:
        bytes_sent = eth_0_stats.bytes_sent
        bytes_recv = eth_0_stats.bytes_recv
        packets_sent = eth_0_stats.packets_sent
        packets_recv = eth_0_stats.packets_recv
        errin = eth_0_stats.errin
        errout = eth_0_stats.errout
        dropin = eth_0_stats.dropin
        dropout = eth_0_stats.dropout

    else:
        # If eth0 does not exist, set them to zero or handle accordingly
        bytes_sent = 0
        bytes_recv = 0
        packets_sent = 0
        packets_recv = 0
        errin = 0
        errout = 0
        dropin = 0
        dropout = 0

    # 3. Build dictionary
    #--------------------------------------------------------------------------
    data = {
        "timestamp": timestamp,
        "cpu_freq_current": cpu_freq,
        "cpu_stats-ctx_switches": ctx_switches,
        "cpu_stats-interrupts": interrupts,
        "cpu_stats-soft_interrupts": soft_interrupts,
        "cpu_stats-syscalls": syscalls,
        "virtual_memory-total": vm_total,
        "virtual_memory-available": vm_available,
        "virtual_memory-percent": vm_percent,
        "virtual_memory-used": vm_used,
        "virtual_memory-free": vm_free,
        "virtual_memory-active": vm_active,
        "virtual_memory-inactive": vm_inactive,
        "virtual_memory-buffers": vm_buffers,
        "virtual_memory-cached": vm_cached,
        "virtual_memory-shared": vm_shared,
        "virtual_memory-slab": vm_slab,
        "n_pids": n_pids,
        "net_io_counters_eth0-bytes_sent": bytes_sent,
        "net_io_counters_eth0-bytes_recv": bytes_recv,
        "net_io_counters_eth0-packets_sent": packets_sent,
        "net_io_counters_eth0-packets_recv": packets_recv,
        "net_io_counters_eth0-errin": errin,
        "net_io_counters_eth0-errout": errout,
        "net_io_counters_eth0-dropin": dropin,
        "net_io_counters_eth0-dropout": dropout,
    }

    # Include each CPU percent individually (cpu_percent-0, cpu_percent-1, etc.)
    for i, cpu_p in enumerate(cpu_percent_list):
        data[f"cpu_percent-{i}"] = cpu_p
    
    # 4. Convert to Json
    #------------------------------------------------------------------------------------
    json_data = json.dumps(data)

    # 5. Store in redis
    r.set("metrics", json_data)
    print(f"Updated Redis key 'metrics' with: {json_data}")


# Main loop to run every five seconds
if __name__ == "__main__":
    while True:
        collect_and_store_metrics()
        time.sleep(5)
