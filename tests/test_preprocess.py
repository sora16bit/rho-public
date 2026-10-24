from rho.preprocess import strip_markdown

def test_removes_fenced_code_block():
    text = "本文です。\n```python\nprint('x')\n```\n続きです。"
    out = strip_markdown(text)
    assert "print" not in out
    assert "本文です。" in out
    assert "続きです。" in out

def test_removes_table_rows():
    text = "見出し\n\n| 列A | 列B |\n|-----|-----|\n| 値1 | 値2 |\n\n本文。"
    out = strip_markdown(text)
    assert "|" not in out
    assert "本文。" in out

def test_removes_heading_line_entirely():
    # 見出しは本文でなく構造ラベルなので、テキストごと落とす(統計に混ぜない)。
    text = "## 章タイトル\n本文。"
    out = strip_markdown(text)
    assert "章タイトル" not in out
    assert "#" not in out
    assert "本文。" in out

def test_removes_horizontal_rule():
    text = "前。\n\n---\n\n後。"
    out = strip_markdown(text)
    assert "前。" in out
    assert "後。" in out
    assert "---" not in out

def test_strips_list_and_quote_markers_keeps_text():
    text = "- りんご\n- みかん\n> 引用文。"
    out = strip_markdown(text)
    assert "りんご" in out
    assert "みかん" in out
    assert "引用文。" in out
    assert not out.strip().startswith("-")
    assert ">" not in out

def test_strips_inline_link_and_emphasis():
    text = "詳しくは[ここ](http://example.com)を見て。**重要**な点。"
    out = strip_markdown(text)
    assert "ここ" in out
    assert "http" not in out
    assert "重要" in out
    assert "*" not in out

def test_plain_text_unchanged():
    text = "ふつうの文章です。記号はそのまま。"
    out = strip_markdown(text)
    assert "ふつうの文章です。" in out
    assert "記号はそのまま。" in out

def test_analyze_drops_markdown_table_no_zero_word_sentence():
    import rho
    md = "解析の説明です。\n\n| 項目 | 値 |\n|------|----|\n| 文長 | 12 |\n\nまとめの文です。"
    doc = rho.analyze(md)
    # 表が「0語の文」として混入していないこと
    for s in doc.sentences:
        assert len(s.content_tokens()) > 0
    # 本文の文は残っている
    joined = "".join(s.text for s in doc.sentences)
    assert "解析の説明です" in joined
    assert "まとめの文です" in joined
    assert "|" not in joined

def test_analyze_drops_headings_from_sentences():
    import rho
    md = "# 設計メモ\n\n本システムは語を切り出す。\n\n## 手法\n\nまとめると要点だ。"
    doc = rho.analyze(md)
    joined = "".join(s.text for s in doc.sentences)
    # 見出しテキストは文として残らない
    assert "設計メモ" not in joined
    assert "手法" not in joined
    # 本文は残る
    assert "本システムは語を切り出す。" in joined
    assert "まとめると要点だ。" in joined
