# scheduler-mcp 修正メモ

## 概要

今回 `sched` の実装まわりで、主に次の 2 点を修正した。

1. Flux jobspec に `GEMINI_API_KEY` などのシェル環境変数が混ざってしまう問題
2. `feasibility.check` の成功時返り値が `null` に見えて、人間にとって判定結果が分かりにくい問題

---

## 1. API キー漏れ修正

### 症状

`JobRequest -> Flux jobspec` の変換結果を確認したとき、jobspec の

- `attributes.system.environment`

の中に、

- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- その他のシェル環境変数

が入っていた。

そのため、jobspec をそのまま出力すると秘密情報が見えてしまっていた。

### 原因

対象ファイル:

- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\scheduler_mcp\transform\convert.py`

`flux.job.JobspecV1.from_command(...)` で jobspec を作ったあと、呼び出し元シェルの環境変数が jobspec 側に残っていた。

### 修正内容

同ファイル内で、jobspec 作成直後に次を必ず設定するようにした。

```python
jobspec.environment = dict(job_request.environment)
```

これにより、

- `JobRequest.environment` に明示した値だけを jobspec に入れる
- 指定がなければ `{}` を入れる

ようにした。

### 修正後の意味

- ユーザが明示していない環境変数は jobspec に含めない
- `GEMINI_API_KEY` のような秘密情報が jobspec 出力に混ざらない

### 確認結果

変換結果の jobspec で、

```json
"environment": {}
```

となることを確認済み。

---

## 2. `feasibility: null` 問題の修正

### 症状

MCP サーバ経由で `check_job_request_sched_feasibility(...)` を呼ぶと、

```json
"feasibility": null
```

となっていた。

これだと、

- 実行可能なのか
- 単に値が取れていないだけなのか

が分かりにくかった。

### 原因

対象ファイル:

- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\scheduler_mcp\sched\feasibility.py`

`flux_sched_resource_feasibility_check(...)` の中で、

```python
raw_response = handle.rpc("feasibility.check", {"jobspec": jobspec_dict}).get()
```

をそのまま扱っていた。

実際に Flux 側を直接確認したところ、

- satisfiable な jobspec
  - `None` を返す
- unsatisfiable な jobspec
  - `OSError("Unsatisfiable request")` を投げる

という挙動だった。

つまり、成功時の `None` がそのまま JSON で `null` に見えていた。

### 修正内容

同ファイルの `flux_sched_resource_feasibility_check(...)` を次のように整理した。

#### 1. 例外が出なかった場合

- `success: true`
- `satisfiable: true`

と返す。

そのうえで、Flux の生返り値は

```python
"feasibility": {
    "satisfiable": True,
    "raw_response": raw_response,
}
```

のように保持する。

#### 2. `Unsatisfiable request` の場合

- ツール失敗ではなく scheduler の判定結果とみなす
- `success: true`
- `satisfiable: false`

を返す。

#### 3. それ以外の本当のエラー

- `success: false`

と返す。

### 修正後の意味

返り値の見方が次のように統一された。

- `success: true, satisfiable: true`
  - 理論上実行可能
- `success: true, satisfiable: false`
  - 理論上実行不可能
- `success: false`
  - 問い合わせ自体が失敗

### 確認結果

#### satisfiable な例

入力例:

- `CPUノード1基を30分使って hostname を実行したい`

結果:

- `satisfiable: true`

#### unsatisfiable な例

入力例:

- `CPUノード4基を1時間使って hostname を実行したい`

結果:

- `satisfiable: false`
- `scheduler_message: "[Errno 19] Unsatisfiable request"`

---

## 3. 補足

今回の `sched` では、次の 2 段階の関数がある。

### 内側

- `flux_sched_resource_feasibility_check(...)`

役割:

- Flux jobspec を直接 scheduler に渡す

### 外側

- `check_job_request_sched_feasibility(...)`

役割:

- `JobRequest -> Flux jobspec` に変換
- そのあと内側の feasibility 関数を呼ぶ
- `job_request` や `conversion_errors` もまとめて返す

そのため、MCP サーバから見える返り値には

- `job_request`
- `jobspec`
- `satisfiable`
- `scheduler_message`
- `feasibility`
- `conversion_errors`

などが含まれる。

---

## 4. 今回修正した主なファイル

- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\scheduler_mcp\transform\convert.py`
- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\scheduler_mcp\sched\feasibility.py`
- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\tests\test_convert.py`
- `C:\Users\ishii makoto\Desktop\lab\scheduler-mcp\tests\test_sched_feasibility.py`

---

## 5. 一言まとめ

今回の修正は、

- **jobspec に秘密情報が混ざらないようにする**
- **scheduler feasibility の結果を `true/false` で読めるようにする**

ためのものだった。
