from multiprocessing import Pool
import os
import time


WORKERS = 4
CHUNK_SIZE = 4_000_000
ROUNDS = 30


def work(seed: int) -> dict:
    total = 0.0
    started_at = time.time()
    for round_idx in range(ROUNDS):
        base = seed + round_idx
        for i in range(CHUNK_SIZE):
            x = (i + base) * 0.000001
            total += x * x
    return {
        "worker_pid": os.getpid(),
        "seed": seed,
        "elapsed_sec": round(time.time() - started_at, 3),
        "result": total,
    }


if __name__ == "__main__":
    print(
        f"parent_pid={os.getpid()} workers={WORKERS} "
        f"chunk_size={CHUNK_SIZE} rounds={ROUNDS}"
    )
    started_at = time.time()
    with Pool(WORKERS) as pool:
        results = pool.map(work, range(WORKERS))
    for item in results:
        print(item)
    print(f"total_elapsed_sec={time.time() - started_at:.3f}")
