from rho.document import Token, Sentence, Document


def _doc(sentences):
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])


# 常体・短文・和語多めの「やわらかい」文書
_SOFT = _doc([
    ("猫が走る。", [Token("猫","猫","名詞",[],"wago"),
                 Token("が","が","助詞",[],"wago"),
                 Token("走る","走る","動詞",[],"wago"),
                 Token("。","。","補助記号",["句点"],"kigou")]),
    ("犬も走る。", [Token("犬","犬","名詞",[],"wago"),
                 Token("も","も","助詞",[],"wago"),
                 Token("走る","走る","動詞",[],"wago"),
                 Token("。","。","補助記号",["句点"],"kigou")]),
])

# 漢語・名詞多め・読点多めの「硬い」文書
_HARD = _doc([
    ("形態素解析を実行する、構造を解析する。", [
        Token("形態素","形態素","名詞",[],"kango"),
        Token("解析","解析","名詞",[],"kango"),
        Token("を","を","助詞",[],"wago"),
        Token("実行","実行","名詞",[],"kango"),
        Token("する","する","動詞",[],"wago"),
        Token("、","、","補助記号",["読点"],"kigou"),
        Token("構造","構造","名詞",[],"kango"),
        Token("を","を","助詞",[],"wago"),
        Token("解析","解析","名詞",[],"kango"),
        Token("する","する","動詞",[],"wago"),
        Token("。","。","補助記号",["句点"],"kigou")]),
])


def test_distance_self_is_zero():
    from rho.compare import distance
    assert distance(_SOFT, _SOFT) == 0.0


def test_distance_differs_for_contrasting_docs():
    from rho.compare import distance
    assert distance(_SOFT, _HARD) > 2.0


def test_standardization_uses_sigma_not_raw():
    # 文長だけ違い他は揃う2文書 → 距離 ≈ 文長差/σ(=12.5)。生差ではない。
    from rho.compare import distance, FEATURE_SCALE
    short = _doc([("猫。", [Token("猫","猫","名詞",[],"wago"),
                          Token("。","。","補助記号",["句点"],"kigou")])])
    # 同じ構成で語数だけ多い文(名詞を増やす)
    long_toks = [Token("猫","猫","名詞",[],"wago") for _ in range(13)]
    long_toks.append(Token("。","。","補助記号",["句点"],"kigou"))
    long = _doc([("猫…。", long_toks)])
    d = distance(short, long)
    # 距離は有限の現実的な値(生の文字数差12ではなく σ で割られている)
    assert 0 < d < 12          # 生差なら12超になるはず。σ標準化で小さくなる
    assert FEATURE_SCALE["avg_sentence_chars"] == 12.5


def test_compare_returns_diffs_and_most_different():
    from rho.compare import compare
    c = compare(_SOFT, _HARD)
    assert "distance" in c
    assert "diffs" in c
    assert "most_different" in c
    # b(_HARD)の方が漢語率が高い → kango_ratio の diff は正
    assert c["diffs"]["kango_ratio"] > 0
    # most_different はトップ3、|差|降順
    md = c["most_different"]
    assert len(md) == 3
    assert abs(md[0][1]) >= abs(md[1][1]) >= abs(md[2][1])


def test_public_api_exports():
    import rho
    assert hasattr(rho, "compare")
    assert hasattr(rho, "distance")
