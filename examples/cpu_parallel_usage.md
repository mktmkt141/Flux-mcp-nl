# cpu_parallel.py の使い方

このサンプルは `multiprocessing.Pool(4)` で 4 プロセスを立てて、各プロセスが重めの数値ループを回します。

自然言語入力例:

```text
CPUノード1基を5分使って、1タスク4CPUで python examples/cpu_parallel.py を実行したい
```

意図:

- `num_tasks = 1`
- `cpus_per_task = 4`
- Python 側で `Pool(4)` を作る

つまり、Flux / scheduler に 4 CPU を確保してもらい、その 1 タスクの中で Python が 4 並列に動きます。
