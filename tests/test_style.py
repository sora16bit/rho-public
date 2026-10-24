from rho.document import Token, Sentence, Document


def _doc(sentences):
    # sentences: list[(text, [Token, ...])]
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])


def test_sentence_style_breakdown_classifies_and_keeps_text():
    from rho.metrics.style import sentence_style_breakdown
    doc = _doc([
        ("です。", [Token("です","です","助動詞",[],"wago"),
                   Token("。","。","補助記号",["句点"],"kigou")]),
        ("作ってる。", [Token("作って","作る","動詞",[],"wago"),
                     Token("る","る","語尾",[],"wago"),
                     Token("。","。","補助記号",["句点"],"kigou")]),
    ])
    r = sentence_style_breakdown(doc)
    assert r["keitai"] == ["です。"]
    assert r["jotai"] == ["作ってる。"]
    assert r["other"] == []
    assert r["mixed"] is True


def test_sentence_style_breakdown_not_mixed():
    from rho.metrics.style import sentence_style_breakdown
    doc = _doc([
        ("です。", [Token("です","です","助動詞",[],"wago"),
                   Token("。","。","補助記号",["句点"],"kigou")]),
    ])
    r = sentence_style_breakdown(doc)
    assert r["mixed"] is False


def _end(text, normalized):
    # 文末が normalized 1語になる単純文を作る
    return (text, [Token(normalized, normalized, "助動詞", [], "wago"),
                   Token("。","。","補助記号",["句点"],"kigou")])


def test_ending_repetition_counts_top_and_streak():
    from rho.metrics.style import ending_repetition
    doc = _doc([
        _end("です1。","です"),
        _end("です2。","です"),
        _end("です3。","です"),
        _end("ます1。","ます"),
    ])
    r = ending_repetition(doc)
    assert r["total"] == 4
    assert r["counts"]["です"] == 3
    assert r["top"] == ("です", 3)
    assert abs(r["top_ratio"] - 0.75) < 1e-9
    assert r["max_streak"]["ending"] == "です"
    assert r["max_streak"]["len"] == 3
    assert r["max_streak"]["sentences"] == ["です1。","です2。","です3。"]


def test_ending_key_uses_surface_tail_not_just_function_word():
    # 「思います」と「します」を区別できること(末尾文字列ベース)。
    # 機能語「ます」だけに潰さない。
    from rho.metrics.style import ending_repetition
    omou = ("Aと思います。", [
        Token("思い","思う","動詞",[],"wago"),
        Token("ます","ます","助動詞",[],"wago"),
        Token("。","。","補助記号",["句点"],"kigou"),
    ])
    suru = ("Bをします。", [
        Token("し","為る","動詞",[],"wago"),
        Token("ます","ます","助動詞",[],"wago"),
        Token("。","。","補助記号",["句点"],"kigou"),
    ])
    doc = _doc([omou, omou, suru])
    r = ending_repetition(doc)
    # 「思います」が最頻(2回)。「します」とは別キー。
    assert r["top"][0] == "思います"
    assert r["top"][1] == 2
    assert "します" in r["counts"]
    assert r["counts"]["します"] == 1


def test_ending_repetition_empty():
    from rho.metrics.style import ending_repetition
    doc = _doc([])
    r = ending_repetition(doc)
    assert r["total"] == 0
    assert r["top"] is None
    assert r["top_ratio"] == 0.0
    assert r["max_streak"]["len"] == 0
    assert r["max_streak"]["ending"] is None


def _words(text, n):
    # 内容語 n 個 + 句点 の文
    toks = [Token("語","語","名詞",[],"kango") for _ in range(n)]
    toks.append(Token("。","。","補助記号",["句点"],"kigou"))
    return (text, toks)


def test_long_sentences_threshold_is_strict_gt():
    from rho.metrics.style import long_sentences
    doc = _doc([_words("ちょうど。", 60), _words("こえた。", 61)])
    r = long_sentences(doc)            # 既定 60、 > 判定
    assert len(r) == 1
    assert r[0]["text"] == "こえた。"
    assert r[0]["words"] == 61


def test_long_sentences_custom_threshold():
    from rho.metrics.style import long_sentences
    doc = _doc([_words("みじかい。", 5), _words("ながい。", 31)])
    r = long_sentences(doc, threshold=30)
    assert [x["text"] for x in r] == ["ながい。"]


def test_style_issues_bundles_three():
    from rho.metrics.style import style_issues
    doc = _doc([
        ("です。", [Token("です","です","助動詞",[],"wago"),
                   Token("。","。","補助記号",["句点"],"kigou")]),
    ])
    r = style_issues(doc)
    assert set(r.keys()) == {"style", "ending", "long"}
    assert r["style"]["keitai"] == ["です。"]


def test_real_article_mixed_and_top_ending():
    import rho
    text = (
        "読んでいただきありがとうございます。私は個人開発をやっています。"
        "個人開発は稼げるフィールドではないと思います。"
        "自分が作りたいと思うままに作ってる。"
        "楽しいので個人開発をしていたいです。"
        "私は概ね賛同します。私はこの説にも概ね賛成します。"
        "もっと稼ぎやすい方法は沢山あると思います。"
    )
    doc = rho.analyze(text)
    si = doc.style_issues()
    assert si["style"]["mixed"] is True            # 敬体と常体がまざる
    assert si["ending"]["top"] is not None
    assert si["ending"]["total"] >= 6
