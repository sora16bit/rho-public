"""profile() / format_profile() のテスト。

summary の算術(mean/std/min/max)は、features() を既知値で差し替えた
軽量スタブで検証する(SudachiPy を回さず profile 固有のロジックだけを試す)。
列キーが FEATURE_SCALE と一致することと、実 Document でも動くことは別に確認する。
"""
import pytest

from rho.compare import FEATURE_SCALE
from rho.document import Token, Sentence, Document


class _StubDoc:
    """features() だけを持つ最小スタブ。与えた値をそのまま返す。"""
    def __init__(self, feats):
        self._feats = feats

    def features(self):
        return dict(self._feats)


def _full(**overrides):
    """FEATURE_SCALE の全キーを 0.0 で埋めた特徴 dict(必要分だけ上書き)。"""
    feats = {k: 0.0 for k in FEATURE_SCALE}
    feats.update(overrides)
    return feats


# --- rows / features の構造 ---

def test_features_keys_match_feature_scale():
    from rho.profile import profile
    result = profile([_StubDoc(_full())])
    assert result["features"] == list(FEATURE_SCALE.keys())


def test_rows_preserve_input_order_and_count():
    from rho.profile import profile
    docs = [
        _StubDoc(_full(kango_ratio=0.1)),
        _StubDoc(_full(kango_ratio=0.2)),
        _StubDoc(_full(kango_ratio=0.3)),
    ]
    result = profile(docs)
    assert [r["kango_ratio"] for r in result["rows"]] == [0.1, 0.2, 0.3]


# --- summary の算術 ---

def test_summary_mean_std_min_max():
    from rho.profile import profile
    # kango_ratio = 0.1, 0.2, 0.3 → mean=0.2, 母std=0.0816..., min=0.1, max=0.3
    docs = [
        _StubDoc(_full(kango_ratio=0.1)),
        _StubDoc(_full(kango_ratio=0.2)),
        _StubDoc(_full(kango_ratio=0.3)),
    ]
    s = profile(docs)["summary"]["kango_ratio"]
    assert s["mean"] == pytest.approx(0.2)
    assert s["std"] == pytest.approx(0.081649658)  # 母標準偏差(n で割る)
    assert s["min"] == pytest.approx(0.1)
    assert s["max"] == pytest.approx(0.3)


def test_single_doc_std_is_zero():
    from rho.profile import profile
    s = profile([_StubDoc(_full(kango_ratio=0.42))])["summary"]["kango_ratio"]
    assert s["mean"] == pytest.approx(0.42)
    assert s["std"] == 0.0
    assert s["min"] == s["max"] == pytest.approx(0.42)


# --- エラー処理 ---

def test_empty_list_raises():
    from rho.profile import profile
    with pytest.raises(ValueError):
        profile([])


# --- format_profile ---

def test_format_profile_contains_rows_and_summary():
    from rho.profile import profile, format_profile
    docs = [_StubDoc(_full(kango_ratio=0.1)), _StubDoc(_full(kango_ratio=0.3))]
    text = format_profile(profile(docs), labels=["A.md", "B.md"])
    assert "A.md" in text and "B.md" in text
    assert "mean" in text and "std" in text


# --- 実 Document との統合(SudachiPy なしで組める最小文書) ---

def _doc(sentences):
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])


def test_profile_works_with_real_documents():
    from rho.profile import profile
    d = _doc([
        ("猫が走る。", [Token("猫", "猫", "名詞", [], "wago"),
                     Token("が", "が", "助詞", [], "wago"),
                     Token("走る", "走る", "動詞", [], "wago"),
                     Token("。", "。", "補助記号", ["句点"], "kigou")]),
    ])
    result = profile([d, d])
    assert len(result["rows"]) == 2
    assert set(result["rows"][0].keys()) == set(FEATURE_SCALE.keys())
