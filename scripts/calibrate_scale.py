"""対照テキスト群から compare.FEATURE_SCALE(各特徴の母σ)を算出する運用ツール。

使い方:
    python scripts/calibrate_scale.py A.txt B.txt C.txt ...

各テキストを rho.analyze → features() で特徴ベクトル化し、特徴ごとの母σを実測。
compare.py へそのまま貼れる FEATURE_SCALE = {...} を標準出力に、警告を標準エラーに出す。

「根拠なき定数を置かない」(学年式の教訓)を距離の土台 FEATURE_SCALE にも適用する。
今の値は5対照テキストの初期見積もりで再現不能だったため、本ツールで作り直せる。
"""
import sys
from pathlib import Path

# scripts/ から rho を import できるようにリポジトリルートを通す
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rho.compare import FEATURE_SCALE
from rho.profile import _column_summary  # 母σの定義を再利用(二重定義しない)

_FEATURES = list(FEATURE_SCALE.keys())


def compute_scale(rows: list) -> dict:
    """features dict のリスト → {特徴: 母σ} の dict。"""
    return {
        key: _column_summary([row[key] for row in rows])["std"]
        for key in _FEATURES
    }


def warnings_for(rows: list, scale: dict) -> list:
    """本数不足・σ=0 を名指しする警告メッセージのリスト(空なら健全)。"""
    msgs = []
    n = len(rows)
    if n < 3:
        msgs.append(f"⚠ {n}本しかない。σが不安定(最低5本推奨)。")
    for key, sigma in scale.items():
        if sigma == 0.0:
            msgs.append(f"⚠ {key} のσ=0(距離計算でゼロ除算になる)。")
    return msgs


def format_scale(scale: dict) -> str:
    """σ dict を compare.py へ貼れる FEATURE_SCALE = {...} 文字列に整形する。"""
    lines = ["FEATURE_SCALE = {  # calibrate_scale.py で実測した母標準偏差"]
    for key in _FEATURES:
        lines.append(f'    "{key}": {round(scale[key], 4)},')
    lines.append("}")
    return "\n".join(lines)


def main(argv: list) -> int:
    if not argv:
        print("使い方: python scripts/calibrate_scale.py A.txt B.txt C.txt ...",
              file=sys.stderr)
        return 1
    import rho
    rows = []
    for path in argv:
        text = Path(path).read_text(encoding="utf-8")
        rows.append(rho.analyze(text).features())
    scale = compute_scale(rows)
    for w in warnings_for(rows, scale):
        print(w, file=sys.stderr)
    print(format_scale(scale))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
