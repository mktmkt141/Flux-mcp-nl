# scheduler-mcp メモ

## 今回やったこと
`flux-mcp` を参考にして、自作 MCP サーバ `scheduler-mcp` を作成した。
目的は、**自然言語のジョブ要求を受け取り、構造化し、Flux の資源状況と照らして実行可能性を返し、最終的に Flux へ投入して結果を観測すること**である。

## 作った機能
1. `parse_natural_language_job_request`  
   自然言語を最小 `JobRequest` に変換する。

2. `get_flux_resource_list`  
   Flux が現在見ている資源を取得する。

3. `check_job_request_feasibility`  
   `JobRequest` と現在の free 資源を比較して、今すぐ実行可能か判定する。

4. `analyze_natural_language_job_request`  
   上の 3 ステップをまとめて実行する統合ツール。

5. `convert_job_request_to_flux_batch_script`  
   `JobRequest` を Flux batch script に変換する。

6. `convert_natural_language_job_request_to_flux_batch_script`  
   自然言語を parse して、そのまま Flux batch script に変換する。

7. `submit_job_request_to_flux`  
   `JobRequest` を Flux batch script に変換し、`flux batch` で submit する。

8. `submit_natural_language_job_request_to_flux`  
   自然言語を parse して、そのまま Flux に submit する。

9. `flux_get_job_info`  
   submit 済みジョブの state / status / result を取得する。

10. `flux_get_job_logs`  
    submit 済みジョブの出力ログを取得する。

## 確認できたこと
- ルールベースで自然言語を `JobRequest` に変換できた。
- `scheduler-mcp` を MCP サーバとして起動できた。
- MCP 経由で各ツールを実際に呼べた。
- Flux コンテナ内の資源情報を取得できた。
- 自然言語入力から、実行可能性判定まで end-to-end で通った。
- `JobRequest` から Flux batch script を生成できた。
- 自然言語入力から、そのまま Flux へ submit できた。
- submit 後の `status` を MCP 経由で確認できた。
- submit 後の `logs` を MCP 経由で確認できた。

## 今の流れ
```text
自然言語
  ↓
parse_natural_language_job_request
  ↓
JobRequest
  ↓
get_flux_resource_list
  ↓
check_job_request_feasibility
  ↓
analyze_natural_language_job_request
  ↓
convert_natural_language_job_request_to_flux_batch_script
  ↓
submit_natural_language_job_request_to_flux
  ↓
flux_get_job_info
  ↓
flux_get_job_logs
```

## 資源情報の意味
返ってきた `nodes`, `cores`, `gpus` は、ローカル PC の物理スペックそのものではない。  
**Docker / WSL を通して Flux コンテナに見えている資源を、Flux セッションが 1 ノード環境として認識した結果**である。

今回の例では:

- `nodes: 1`  
  `flux start --test-size=1` で 1 ノードのテスト環境を作ったため。
- `cores: 4`  
  コンテナから見えている CPU コア数。
- `gpus: 0`  
  GPU をコンテナに渡していないため。

## submit / status / logs で分かったこと
- `submit` は実際に Flux へジョブ投入しており、`job_id` が返る。
- `status` では、ジョブの `state`, `status`, `result`, `returncode`, `runtime` などを確認できる。
- `logs` では、ジョブの標準出力を取得できる。
- 今回の `hostname` ジョブでは、`logs` の `lines` に `ce88e08a04d2` が返り、実際にコンテナ内でコマンドが実行されたことを確認できた。

## 時間指定の注意
`wall_time` は `JobRequest` 内では秒で持っている。  
Flux script に変換するときは、Flux 側で分として誤解されないよう、`# flux: -t 1800s` のように **秒の単位 `s` を付ける必要がある**。

## 研究上の意味
ここまでで、研究の最初の土台として

- 人間の自然言語入力
- 構造化ジョブ要求への変換
- 資源状況の取得
- 実行可能性の初期判定
- Flux 向け script 生成
- Flux への投入
- 投入後の状態確認
- 投入後の出力確認

まで作れた。

つまり、将来的に LLM / AI エージェントを入れるとしても、  
**差し替える主な場所は「自然言語 -> JobRequest」の部分**だと整理できる。

## 次の候補
- `JobRequest` の項目を増やす。
- LLM を差し込む設計を整理する。
- 研究用の図や説明資料に落とす。

## Gemini 版で追加したこと
- `parse_natural_language_job_request_with_gemini`
  Gemini API を使って自然言語を `JobRequest` に変換する。
- `analyze_natural_language_job_request_with_gemini`
  Gemini で parse した `JobRequest` をそのまま feasibility 判定に流す。
- `submit_natural_language_job_request_to_flux_with_gemini`
  Gemini で parse した結果をそのまま Flux へ submit する。

## Gemini 版で確認できたこと
- `GEMINI_API_KEY` を Flux コンテナ側の起動シェルにだけ設定する運用で、秘密情報をファイルに残さず利用できた。
- 自然言語を Gemini に渡して `JobRequest` を生成できた。
- 生成した `JobRequest` から Flux batch script を作れた。
- Gemini 版の submit でも `job_id` が返り、実際に Flux へ投入できた。
- 例: `submit_natural_language_job_request_to_flux_with_gemini` で `hostname` ジョブを投入し、`job_id` と script を取得できた。

## 端末から自然言語を試す方法
Gemini 版の自然言語 submit は、ローカル WSL 側で次の example から直接試せる。

```bash
python examples/run_gemini_submit_from_terminal.py "1ノードで30分使って hostname を実行したい"
```

引数を付けない場合は対話入力になる。
