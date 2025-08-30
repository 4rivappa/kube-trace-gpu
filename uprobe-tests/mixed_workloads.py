import torch
import time
import random

assert torch.cuda.is_available(), "CUDA is not available"

while True:
    rows = random.randint(2000, 12000)
    cols = random.randint(2000, 12000)

    print(f"Generating {rows}x{cols} tensor on CPU...")

    cpu_tensor = torch.randn(rows, cols, dtype=torch.float32)

    gpu_tensor = cpu_tensor.to("cuda", non_blocking=True)
    gpu_sum = gpu_tensor.sum()
    cpu_sum = gpu_sum.to("cpu", non_blocking=True)

    torch.cuda.synchronize()

    print(f"Sum of elements: {cpu_sum.item():.4f}")

    time.sleep(random.uniform(2, 5))
