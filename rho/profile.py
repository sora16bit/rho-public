"""複数文章の特徴量を一覧表にして傾向を俯瞰する。compare(2本) の N 本版。

profile() は機械可読な dict(rows + 列ごとの統計 summary)を返し、
人間向けの罫線表は format_profile() に分ける(compare と同じ哲学)。

列の並びは compare.FEATURE_SCALE のキー順を唯一の真実として再利用する。
→ profile と compare で特徴セットが必ず一致する(二重定義しない)。
"""

from rho.compare import FEATURE_SCALE

_FEATURES = list(FEATURE_SCALE.keys())


def _column_summary(values: list) -> dict:
    """1 列分の mean / std(母標準偏差) / min / max。"""
    n = len(values)
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n  # n で割る母分散
    return {"mean": mean, "std": var ** 0.5, "min": min(values), "max": max(values)}


def profile(docs: list) -> dict:
    """複数 Document の特徴量を一覧 + 列ごとの統計でまとめる。

    戻り値: {"features": [...], "rows": [features dict, ...], "summary": {key: {...}}}
    空リストは ValueError。
    """
    if not docs:
        raise ValueError("profile() needs at least one document")
    rows = [d.features() for d in docs]
    summary = {
        key: _column_summary([row[key] for row in rows])
        for key in _FEATURES
    }
    return {"features": list(_FEATURES), "rows": rows, "summary": summary}


def format_profile(result: dict, labels: list = None) -> str:
    """profile() の結果を人間向けの罫線表に整形する。

    各行が 1 記事(labels で名前付け)、列が特徴量。最下部に mean / std 行。
    """
    features = result["features"]
    rows = result["rows"]
    summary = result["summary"]
    labels = labels or [f"#{i}" for i in range(len(rows))]

    label_w = max([len("statistic")] + [len(str(l)) for l in labels])
    col_w = {f: max(len(f), 7) for f in features}

    def fmt_row(name: str, getter) -> str:
        cells = " ".join(f"{getter(f):>{col_w[f]}.3g}" for f in features)
        return f"{name:<{label_w}}  {cells}"

    header = f"{'':<{label_w}}  " + " ".join(f"{f:>{col_w[f]}}" for f in features)
    lines = [header]
    for label, row in zip(labels, rows):
        lines.append(fmt_row(str(label), lambda f, r=row: r[f]))
    lines.append("-" * len(header))
    lines.append(fmt_row("mean", lambda f: summary[f]["mean"]))
    lines.append(fmt_row("std", lambda f: summary[f]["std"]))
    return "\n".join(lines)
