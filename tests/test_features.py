from rho.document import Token, Sentence, Document


def _doc(sentences):
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])


def test_features_are_flat_scalars():
    from rho.features import extract_features
    doc = _doc([
        ("猫が走る、犬も走る。", [
            Token("猫","猫","名詞",[],"kango"),
            Token("が","が","助詞",[],"wago"),
            Token("走る","走る","動詞",[],"wago"),
            Token("、","、","補助記号",["読点"],"kigou"),
            Token("犬","犬","名詞",[],"wago"),
            Token("も","も","助詞",[],"wago"),
            Token("走る","走る","動詞",[],"wago"),
            Token("。","。","補助記号",["句点"],"kigou"),
        ]),
    ])
    f = extract_features(doc)
    # 全 value がスカラー(ネストなし)
    for k, v in f.items():
        assert isinstance(v, (int, float)), f"{k} is not scalar: {v!r}"
    # 必須キーが揃う
    for k in ("kango_ratio", "wago_ratio", "gairaigo_ratio", "noun_ratio",
              "hiragana_ratio", "avg_sentence_chars", "avg_sentence_words",
              "predicates_per_sentence", "keitai_ratio", "jotai_ratio",
              "mtld", "comma_per_sentence"):
        assert k in f


def test_comma_per_sentence():
    from rho.features import extract_features
    doc = _doc([
        ("あ、い、う。", [
            Token("あ","あ","名詞",[],"wago"),
            Token("、","、","補助記号",["読点"],"kigou"),
            Token("い","い","名詞",[],"wago"),
            Token("、","、","補助記号",["読点"],"kigou"),
            Token("う","う","名詞",[],"wago"),
            Token("。","。","補助記号",["句点"],"kigou"),
        ]),
        ("え。", [
            Token("え","え","名詞",[],"wago"),
            Token("。","。","補助記号",["句点"],"kigou"),
        ]),
    ])
    f = extract_features(doc)
    assert f["comma_per_sentence"] == 1.0   # 読点2 / 文2


def test_jotai_only_document():
    # 文末辞書(_JOTAI_END)が判定できる常体語尾を使う(「だ/である/た/る」等)。
    from rho.features import extract_features
    doc = _doc([
        ("猫である。", [Token("猫","猫","名詞",[],"kango"),
                     Token("で","で","助動詞",[],"wago"),
                     Token("ある","ある","動詞",[],"wago"),
                     Token("。","。","補助記号",["句点"],"kigou")]),
        ("走る。", [Token("走る","走る","動詞",[],"wago"),
                  Token("。","。","補助記号",["句点"],"kigou")]),
    ])
    f = extract_features(doc)
    assert f["jotai_ratio"] == 1.0
    assert f["keitai_ratio"] == 0.0


def test_empty_document_no_crash():
    from rho.features import extract_features
    doc = _doc([])
    f = extract_features(doc)
    assert f["comma_per_sentence"] == 0.0
    assert f["keitai_ratio"] == 0.0
    for v in f.values():
        assert isinstance(v, (int, float))


def test_features_shortcut():
    from rho.document import Token, Sentence, Document
    s = Sentence("走る。", [Token("走る","走る","動詞",[],"wago"),
                         Token("。","。","補助記号",["句点"],"kigou")])
    doc = Document(raw="走る。", lang="ja", sentences=[s], paragraphs=[[s]])
    assert "kango_ratio" in doc.features()
