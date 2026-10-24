"""2つの文章の構造的特徴がどれだけ違うかを標準化距離で出す。

features() は率(0〜1)と量(文長・MTLD)を混在させており、素の距離だと
スケールの大きい量が支配する。各特徴を典型的なばらつき(σ)で割って
「σ何個分ずれているか」に揃えてから距離を測る(z標準化)。

FEATURE_SCALE は開発時に設定した暫定値。元の対照テキストは公開版に
含まれず、この値の算出過程は公開版だけでは再現できない。
scripts/calibrate_scale.py で用途に合う公開可能な文章から再計算できる。
距離は文章の意味の類似度や品質を保証する尺度ではない。
"""

FEATURE_SCALE = {  # 開発時の暫定尺度。算出元コーパスは非同梱。
    "kango_ratio": 0.12,
    "wago_ratio": 0.15,
    "gairaigo_ratio": 0.03,
    "noun_ratio": 0.09,
    "hiragana_ratio": 0.21,
    "avg_sentence_chars": 12.5,
    "avg_sentence_words": 7.4,
    "predicates_per_sentence": 1.3,
    "keitai_ratio": 0.30,
    "jotai_ratio": 0.36,
    "mtld": 15.0,
    "comma_per_sentence": 0.65,
}


def _sigma_diffs(doc_a, doc_b) -> dict:
    """各特徴の差を σ で割った符号付き値(fb - fa)/σ。"""
    fa, fb = doc_a.features(), doc_b.features()
    return {k: (fb[k] - fa[k]) / scale for k, scale in FEATURE_SCALE.items()}


def distance(doc_a, doc_b) -> float:
    """標準化ユークリッド距離。同一の特徴ベクトルなら 0.0。"""
    diffs = _sigma_diffs(doc_a, doc_b)
    total = sum(d * d for d in diffs.values())
    return round(total ** 0.5, 3)


def compare(doc_a, doc_b) -> dict:
    """距離 + 特徴ごとの σ単位の差 + 最も違う特徴トップ3 を返す。"""
    diffs = _sigma_diffs(doc_a, doc_b)
    total = sum(d * d for d in diffs.values())
    most = sorted(diffs.items(), key=lambda kv: abs(kv[1]), reverse=True)[:3]
    return {
        "distance": round(total ** 0.5, 3),
        "diffs": diffs,
        "most_different": most,
    }
