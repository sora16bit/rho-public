# Rho

**日本語の文章を測り、特徴を説明するPythonライブラリ・CLI。実験的 v0.1.0。**

文章の長さ、語彙の豊かさ、品詞や表記の傾向、敬体・常体の混在、語尾の繰り返しを調べます。数値だけでなく、該当する文や説明をたどれることを重視しています。

Webアプリや完成したプログラミング言語ではなく、文章分析のための試作です。解析はSudachiPyとローカル辞書で実行し、LLMのAPIキーは不要です。

## できること

- 文・段落・語の数、文長の分布を調べる
- 語彙の豊かさ（MTLD）、品詞・ひらがな等の比率を調べる
- 敬体と常体の混在、語尾の反復、長い文を該当箇所とともに確認する
- 説明文形式または数値表形式のレポートを出す
- 複数の文章の特徴を比較し、文体プロフィールやクラスタを作る（実験的）

## インストール

Python 3.12以上を使用します。初回インストールではSudachiの辞書も取得するため、ネットワーク接続が必要です。

```bash
git clone https://github.com/sora16bit/rho-public.git
cd rho-public
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

WindowsのPowerShellでは、仮想環境の有効化に `.venv\Scripts\Activate.ps1` を使います。PyPIへは公開していないため、このリポジトリからインストールしてください。

## CLIで使う

```bash
rho analyze examples/sample.txt
rho analyze examples/sample.txt --raw
```

UTF-8のテキストファイルを指定します。Markdownの基本的な記法は解析前に取り除きます。標準入力も利用できます。

```bash
echo '私は本を読みます。感想を書きます。今日は良い日だった。' | rho analyze -
```

[サンプル入力](examples/sample.txt)と[実行結果](examples/sample-report.txt)を収録しています。辞書のバージョンによって結果は変わり得ます。生成時のバージョンは[検証記録](VALIDATION.md)に記載します。

## Pythonから使う

```python
import rho

doc = rho.analyze("私は本を読みます。感想を書きます。今日は良い日だった。")
print(doc.report())                  # 説明文形式のレポート
print(doc.report(mode="raw"))        # 数値表形式
metrics = doc.report_dict()          # 構造化した結果
issues = doc.style_issues()          # 敬体・常体、語尾の傾向
long_sentences = doc.long_sentences(threshold=30)
```

ファイルからは `rho.load("examples/sample.txt")` で読み込めます。より詳しい利用例は `try_rho.py`、`compare_rho.py`、`profile_rho.py`、`cluster_rho.py` を参照してください。

## 指標の限界と未実装の機能

- 語種の分類や文節数には、文字種・品詞等に基づく近似を含みます。
- MTLD等の指標は文章の長さや形態素解析結果の影響を受けます。文章の良し悪しを一つの値で判定するためのものではありません。
- 単一の可読性・学年スコアは出しません。開発時に学年推定式の近似を試しましたが、前提となる解析が異なり、文章間の難易度の順序が逆転したため撤回しました。
- `compare` の標準化尺度 `FEATURE_SCALE` は暫定値です。算出元の個人用コーパスは同梱していないため、公開版だけでは元の算出過程を再現できません。`scripts/calibrate_scale.py` で手元の比較対象から尺度を計算できます。距離は意味の類似度や著者の同一性を保証しません。
- `doc.advise()` によるLLMの講評は未実装で、呼び出すと `NotImplementedError` になります。`rho.advise.build_context()` は入力材料を作るだけで、外部APIを呼びません。
- レポート内の説明は指標をもとにしたルールによるものです。汎用的な意味理解や自動校正ではありません。

## 構成

```text
rho/                 解析・指標・レポート・比較の実装
tests/               ユニットテスト
scripts/             比較尺度の計算ツール
examples/            公開用のサンプル入力と出力
try_rho.py           単一文章の分析例
compare_rho.py       二つの文章の比較例
profile_rho.py       複数文章のプロフィール例
cluster_rho.py       複数文章のクラスタリング例
```

## テスト

```bash
python -m pytest -q
```

[検証記録](VALIDATION.md)に公開準備時の結果を記載しています。

## この公開版について

個人開発Rhoのソースコード公開用スナップショットです。実装・テスト・利用例を収録し、個人用コーパス、開発会話、作業環境の設定、元の非公開リポジトリの履歴は含めていません。開発にはAIを活用しています。

作成者: [sora16bit](https://github.com/sora16bit)
