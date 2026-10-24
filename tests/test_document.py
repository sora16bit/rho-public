from rho.document import Token, Sentence, Document

def test_token_fields():
    tok = Token(surface="猫", normalized="猫", pos="名詞",
                pos_detail=["普通名詞"], goshu="kango")
    assert tok.surface == "猫"
    assert tok.pos == "名詞"
    assert tok.goshu == "kango"

def test_document_counts():
    s1 = Sentence(text="猫だ。", tokens=[
        Token("猫", "猫", "名詞", ["普通名詞"], "kango"),
        Token("だ", "だ", "助動詞", [], "wago"),
        Token("。", "。", "補助記号", ["句点"], "kigou"),
    ])
    doc = Document(raw="猫だ。", lang="ja",
                   sentences=[s1], paragraphs=[[s1]])
    assert doc.sentence_count() == 1
    assert doc.paragraph_count() == 1
    # 記号を除いた語数
    assert doc.word_count() == 2
    assert len(doc.all_tokens()) == 3

def test_word_count_excludes_symbols():
    s = Sentence(text="あ、い。", tokens=[
        Token("あ","あ","感動詞",[],"wago"),
        Token("、","、","補助記号",["読点"],"kigou"),
        Token("い","い","名詞",[],"wago"),
        Token("。","。","補助記号",["句点"],"kigou"),
    ])
    doc = Document(raw="あ、い。", lang="ja", sentences=[s], paragraphs=[[s]])
    assert doc.word_count() == 2

def test_public_api_analyze_and_report():
    import rho
    doc = rho.analyze("吾輩は猫である。名前はまだ無い。")
    assert doc.sentence_count() == 2
    assert isinstance(doc.report(), str)
    assert doc.mtld() >= 0

def test_public_api_load(tmp_path):
    import rho
    p = tmp_path / "a.md"
    p.write_text("猫である。犬もいる。", encoding="utf-8")
    doc = rho.load(str(p))
    assert doc.sentence_count() == 2

def test_hiragana_ratio_shortcut():
    from rho.document import Token, Sentence, Document
    s = Sentence("猫が走る", [
        Token("猫","猫","名詞",[],"kango"),
        Token("が","が","助詞",[],"wago"),
        Token("走る","走る","動詞",[],"wago"),
    ])
    doc = Document(raw="猫が走る", lang="ja", sentences=[s], paragraphs=[[s]])
    assert isinstance(doc.hiragana_ratio(), float)
    # 撤回した合成スコアのショートカットは存在しない
    assert not hasattr(doc, "grade_level")
    assert not hasattr(doc, "jreadability")

def test_style_shortcuts():
    from rho.document import Token, Sentence, Document
    s = Sentence("です。", [Token("です","です","助動詞",[],"wago"),
                          Token("。","。","補助記号",["句点"],"kigou")])
    doc = Document(raw="です。", lang="ja", sentences=[s], paragraphs=[[s]])
    assert "style" in doc.style_issues()
    assert isinstance(doc.long_sentences(), list)

def test_long_sentences_shortcut_passes_threshold():
    from rho.document import Token, Sentence, Document
    toks = [Token("語","語","名詞",[],"kango") for _ in range(31)]
    toks.append(Token("。","。","補助記号",["句点"],"kigou"))
    s = Sentence("ながい。", toks)
    doc = Document(raw="ながい。", lang="ja", sentences=[s], paragraphs=[[s]])
    # 既定60だと該当なし、threshold=30 だと該当1件
    assert doc.long_sentences() == []
    assert doc.long_sentences(threshold=30)[0]["words"] == 31
