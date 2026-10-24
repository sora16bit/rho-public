from rho.analyzer.sudachi_ja import SudachiJaAnalyzer

def test_analyze_splits_sentences():
    a = SudachiJaAnalyzer()
    doc = a.analyze("吾輩は猫である。名前はまだ無い。")
    assert doc.lang == "ja"
    assert doc.sentence_count() == 2

def test_analyze_tokens_have_pos_and_goshu():
    a = SudachiJaAnalyzer()
    doc = a.analyze("国際会議でコンピューターを見た。")
    surfaces = {t.surface: t for t in doc.all_tokens()}
    assert surfaces["国際"].pos == "名詞"
    assert surfaces["国際"].goshu == "kango"
    assert surfaces["コンピューター"].goshu == "gairaigo"
    assert surfaces["で"].pos == "助詞"

def test_analyze_paragraphs_by_blank_line():
    a = SudachiJaAnalyzer()
    doc = a.analyze("一文目だ。\n\n二段落目だ。次の文だ。")
    assert doc.paragraph_count() == 2

def test_empty_text_is_safe():
    a = SudachiJaAnalyzer()
    doc = a.analyze("")
    assert doc.sentence_count() == 0
    assert doc.word_count() == 0
