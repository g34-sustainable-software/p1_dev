import time

def cpu_warmup(duration_seconds=300):  # 300s = 5 minutes
    print(f"Running CPU warmup for {duration_seconds} seconds...")
    start = time.time()
    while time.time() - start < duration_seconds:
        a, b = 0, 1
        for _ in range(100000):
            a, b = b, a + b
    print("CPU warmup done.")

if __name__ == "__main__":
    cpu_warmup(duration_seconds=300)