import os
import socket
import time
from bcc import BPF
from prometheus_client import start_http_server, Gauge, Counter


libcudart_path = "/home/arivappa/personal/gpu-trace/lib/python3.12/site-packages/nvidia/cuda_runtime/lib/libcudart.so.12"

node_name = socket.gethostname()
bpf_text = None


current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "program.bpf.c"), "r") as f:
    bpf_text = f.read()

b = BPF(text=bpf_text)
b.attach_uprobe(name=libcudart_path, sym="cudaLaunchKernel", fn_name="trace_cuda_launch_kernel")
b.attach_uprobe(name=libcudart_path, sym="cudaMemcpyAsync", fn_name="trace_cuda_memcpy_async")

kind_map = {
    1: "HostToDevice",
    2: "DeviceToHost",
    3: "DeviceToDevice",
    4: "Default"
}


host_to_device_gauge = Gauge(
    "cuda_host_to_device_bytes",
    "Current total bytes transferred from host to device",
    ["node"]
)

device_to_host_gauge = Gauge(
    "cuda_device_to_host_bytes",
    "Current total bytes transferred from device to host",
    ["node"]
)

kernel_launches = Counter(
    "cuda_kernel_launches_total",
    "Total number of CUDA kernel launches",
    ["node"]
)

current_host_to_device_bytes = 0
current_device_to_host_bytes = 0


def handle_mem_cpy_event(cpu, data, size):
    print("handle_mem_cpy_event method call")
    global current_host_to_device_bytes, current_device_to_host_bytes
    event = b["events"].event(data)
    kind_str = kind_map.get(event.kind, f"Unknown({event.kind})")

    if kind_str == "HostToDevice":
        print(f"HostToDevice: {event.size}")
        current_host_to_device_bytes += event.size
    elif kind_str == "DeviceToHost":
        print(f"DeviceToHost: {event.size}")
        current_device_to_host_bytes += event.size


def update_guage_metrics():
    global current_host_to_device_bytes, current_device_to_host_bytes

    host_to_device_gauge.labels(node=node_name).set(current_host_to_device_bytes)
    device_to_host_gauge.labels(node=node_name).set(current_device_to_host_bytes)

    current_host_to_device_bytes = 0
    current_device_to_host_bytes = 0


def update_kernel_launches():
    counts = b.get_table("kernel_count")
    total_launches = sum(v.value for v in counts.values())
    if total_launches > 0:
        kernel_launches.labels(node=node_name).inc(total_launches)
        counts.clear()

b["events"].open_perf_buffer(handle_mem_cpy_event)

start_http_server(9100)
print(f"Metrics server started on :9100 for node {node_name}")

try:
    b.perf_buffer_poll()
    while True:
        b.perf_buffer_poll()
        update_guage_metrics()
        update_kernel_launches()
        time.sleep(2)
except KeyboardInterrupt:
    print("Stopping...")
