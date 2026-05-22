import os
import time


ITERATIONS = 8_000_000


if __name__ == "__main__":
    started_at = time.time()
    total = 0.0
    for i in range(ITERATIONS):
        x = (i + 1) * 0.000001
        total += x * x
    print(f"pid={os.getpid()} iterations={ITERATIONS} result={total}")
    print(f"elapsed_sec={time.time() - started_at:.3f}")
