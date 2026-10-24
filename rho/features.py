"""文章の構造的特徴を機械可読なスカラー dict(特徴ベクトル)で返す。

Rho = 文章のデータマイニング。report() が人間向けの表示なのに対し、
features() は機械が食う素材 — 比較・分類・蓄積に直結するフラットな数値辞書。

率は 0〜1、量は生値で混在させる(距離計算時のスケーリングは使う側の責任)。
話題語(名詞の中身)は入れない。構造的特徴に徹する。
計算は既存メトリクスに委譲し、ここは集約のみ(read.build_report と同じ役割)。
"""


def _comma_per_sentence(doc) -> float:
    """読点「、」の頻度(読点数 ÷ 文数)。文の区切り方の癖。文数0なら0.0。"""
    if not doc.sentences:
        return 0.0
    commas = sum(1 for t in doc.all_tokens() if t.surface == "、")
    return commas / doc.sentence_count()


def extract_features(doc) -> dict:
    """文章の構造的特徴をフラットなスカラー dict で返す。"""
    from rho.metrics.universal import basic_counts, mtld
    from rho.metrics.japanese import (
        goshu_ratio, pos_ratio, hiragana_ratio,
        chars_per_sentence, predicates_per_sentence, sentence_end_style,
    )
    g = goshu_ratio(doc)
    p = pos_ratio(doc)
    se = sentence_end_style(doc)
    se_total = se["keitai"] + se["jotai"] + se["other"]
    return {
        "kango_ratio": g["kango"],
        "wago_ratio": g["wago"],
        "gairaigo_ratio": g["gairaigo"],
        "noun_ratio": p.get("名詞", 0.0),
        "hiragana_ratio": hiragana_ratio(doc) / 100,
        "avg_sentence_chars": chars_per_sentence(doc),
        "avg_sentence_words": basic_counts(doc)["avg_sentence_length"],
        "predicates_per_sentence": predicates_per_sentence(doc),
        "keitai_ratio": se["keitai"] / se_total if se_total else 0.0,
        "jotai_ratio": se["jotai"] / se_total if se_total else 0.0,
        "mtld": mtld(doc),
        "comma_per_sentence": _comma_per_sentence(doc),
    }
