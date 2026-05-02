# DataOps Agent 実践化ディスカッション

## 参加者

- B: 既存コードと開発体験を見ながら、短期で実装可能な改善順を整理。
- A: 別エージェントとして、実務利用時のリスクと不足機能を独立にレビュー。

## 初回の合意点

1. SQL ツールは読み取り専用をデフォルトにする。
   現状の `SQLQueryTool` は `INSERT`、`UPDATE`、`DELETE`、`DROP`、`ALTER` なども抽出対象になっており、実務利用では危険。まず `SELECT` と `WITH` のみ許可し、書き込み系は明示的な別モードに分けるべき。

2. SQL 実行には制限と監査情報が必要。
   無制限クエリ、巨大な結果セット、長時間実行、実行履歴なしの状態は DataOps 用途では扱いづらい。行数上限、実行時間、SQL の記録、失敗理由の整備を優先する。

3. スキーマ探索ツールを追加する。
   自然言語から直接 SQL 生成に入る前に、テーブル一覧、カラム、外部キー、サンプル行を安全に確認できる導線が必要。これは LLM の推測を減らし、回答品質にも直結する。

4. テスト基盤を先に作る。
   `pyproject.toml` には pytest 設定があるが `tests/` がない。SQL 抽出、SQL ガード、CLI 応答整形、設定 override を最初のユニットテスト対象にする。

5. README と CLI の実装差分をなくす。
   README は notes や temperature のオプションに触れているが、現状 CLI には `--interactive` と `--verbose` しかない。実装するか、ドキュメントを実態に合わせる必要がある。

6. 依存関係と `.env.example` を整理する。
   SQL support は `langchain-classic` を要求する可能性があるが依存に入っていない。`.env.example` の inline comment 付き値も設定事故の原因になり得る。

## 意見が分かれそうな点

### 破壊的操作を将来サポートするか

B の見解:
まずは読み取り専用に固定する。DataOps agent であっても、SQL の書き込みやジョブ再実行は確認フロー、権限、監査ログが揃ってからでよい。

A の見解:
実務価値として dbt、Airflow、Dagster などの操作系ツールは重要。ただし再実行や変更操作は明示確認なしに実行しない設計が必要。

暫定結論:
短期ロードマップでは read-only analytics agent として固める。操作系は設計だけ README/PLAN に残し、実装は後続フェーズにする。

### ノート保存をどこまで構造化するか

B の見解:
現状の `notes.md` 追記はスターターとして十分だが、監査や検索には弱い。先に SQL 安全性とテストを優先する。

A の見解:
会話履歴、ノート、実行履歴はセッション単位で保存できるほうが実務的。SQLite/Postgres backend の切替を検討できる。

暫定結論:
当面は notes は維持し、SQL 実行ログだけ構造化しやすい形で追加する。ノート backend の抽象化は後回し。

## 提案ロードマップ

### Phase 1: 安全な SQL アシスタント化

- `SQLQueryTool` を read-only にする。
- `SELECT` / `WITH` 以外の直接 SQL と LLM 生成 SQL を拒否する。
- SQL 抽出と拒否条件のテストを追加する。
- README に read-only の前提を明記する。

### Phase 2: 実務的なクエリ実行

- 結果行数上限を設定化する。
- 実行 SQL、実行時間、結果件数、エラーをログに残す。
- 長すぎる結果を要約し、必要なら再クエリを促す。
- `.env.example` と依存関係を整理する。

### Phase 3: スキーマ探索

- テーブル一覧ツールを追加する。
- カラム、型、外部キー、サンプル行を返すツールを追加する。
- SQL 生成前にスキーマ確認を促す system prompt に更新する。

### Phase 4: DataOps 運用ツール

- dbt manifest / run results の読み取りツールを追加する。
- Airflow / Dagster などはまず状態確認だけ対応する。
- 再実行や変更操作は明示確認と監査ログ付きで別フェーズにする。

## 次に着手するなら

最初の実装候補は `SQLQueryTool` の read-only 化と `tests/` 新設。理由は、実務上のリスクを最も早く下げられ、後続のスキーマ探索や監査ログ追加の土台にもなるため。

## A の追加レビュー

1. `WITH` を単純に read-only 扱いするのは危険。
   Postgres では writable CTE により、先頭が `WITH` でも `INSERT` / `UPDATE` / `DELETE` を含む SQL が成立する。Phase 1 の SQL ガードは先頭キーワードだけで判定せず、文全体に書き込み系キーワードが含まれる場合は拒否する。可能なら SQL パーサーを使い、コメントや文字列中の単語で誤判定しない実装にする。

2. read-only はアプリ側ガードだけに依存しない。
   `SQLQueryTool` の拒否条件は必要だが、実務運用では DB ユーザー自体を読み取り専用権限にするほうが安全。README には `DATABASE_URL` に read-only user を使う前提を明記し、ローカル Postgres でも分析用ユーザーを分ける案を検討する。

3. SQL 依存関係の整理は Phase 1 に含める。
   現状は `DATABASE_URL` を設定すると `langchain-classic` 不足で SQL support が起動時に落ちる可能性がある。read-only 化に着手する前提として、`pyproject.toml` と README の SQL 依存説明を先に揃える。

## B から A への反論

1. `WITH` の危険性は同意するが、単純な全文キーワード拒否だけでは不足。
   writable CTE を考えると `WITH` を先頭キーワードだけで許可するのは危険。ただし、文全体に `INSERT` / `UPDATE` / `DELETE` が含まれるだけで拒否すると、コメントや文字列中の単語でも誤検知する。Phase 1 では保守的な拒否でもよいが、実用化するなら `sqlglot` などの SQL パーサー導入を検討する。

2. read-only DB ユーザーは必要だが、導入順は分ける。
   本番や共有 DB では read-only user を必須にするべき。一方で、ローカル `compose.yaml` まで最初からユーザー分離すると初期実装が重くなる。まず README と `.env.example` に read-only user 前提を明記し、アプリ側ガードを入れた後、ローカル Postgres の分析用ユーザー分離を後続で扱う。

3. `langchain-classic` 整理は必要だが、read-only ガードの前提にはしない。
   依存関係の整理は必要だが、Phase 1 の範囲を広げすぎると安全対策の着手が遅れる。最小の Phase 1 は、既存 SQL ツールが起動できる環境で危険 SQL を拒否し、その拒否条件をテストするところまでにする。依存追加と README 整理は同じ PR でもよいが、read-only ガード実装とは分けて考える。

B の優先順位:

1. SQL ガードを read-only にする。
2. writable CTE を考慮して `WITH` の判定を強める。
3. SQL 抽出と拒否条件のテストを追加する。
4. README に read-only DB user 前提を書く。
5. 依存関係整理とローカル DB user 分離は同時または次フェーズで扱う。

## A としての最終結論

B の反論を踏まえると、最初の実装範囲は安全対策に絞るのが妥当。A の懸念は維持するが、Phase 1 を大きくしすぎると read-only 化そのものが遅れるため、依存関係整理やローカル DB ユーザー分離は同一 PR の任意タスクまたは直後のタスクに分ける。

最終的な Phase 1 の結論:

1. `SQLQueryTool` は read-only のみ許可する。
2. 許可する SQL は実質的に `SELECT` 系に限定し、`WITH` は writable CTE を考慮して慎重に扱う。
3. Phase 1 の初期実装では保守的な拒否条件でよいが、文字列やコメントによる誤検知を避けるため、実用化前に `sqlglot` などの SQL パーサー導入を検討する。
4. SQL 抽出、直接 SQL、LLM 生成 SQL、writable CTE、複数文、コメント混入の拒否テストを追加する。
5. README と `.env.example` には、本番・共有 DB では read-only DB user を使う前提を明記する。

依存関係整理の扱い:

- `langchain-classic` の不足は実運用上の問題なので放置しない。
- ただし read-only ガードの実装ブロッカーにはせず、同じ PR の小さな追加修正か Phase 1.5 として扱う。
- ローカル Postgres の read-only user 分離は、README に方針を書いた後で Phase 2 以降に実装する。

したがって、次に着手する作業は「SQL ガードとテスト」で確定する。README の read-only user 前提は同時に入れるが、依存追加と compose のユーザー分離は後続に回してよい。
