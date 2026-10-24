from rho.document import Token, Sentence, Document


def _doc(sentences, raw):
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw=raw, lang="ja", sentences=sents, paragraphs=[sents])


def test_build_context_bundles_text_metrics_and_style():
    from rho.advise import build_context
    doc = _doc(
        [("です。", [Token("です","です","助動詞",[],"wago"),
                    Token("。","。","補助記号",["句点"],"kigou")])],
        raw="です。",
    )
    ctx = build_context(doc)
    # LLM に渡す材料が1つの dict に揃っている
    assert ctx["text"] == "です。"
    assert ctx["lang"] == "ja"
    assert "metrics" in ctx            # report_dict 相当
    assert "style" in ctx["metrics"]["style_issues"]


def test_advise_without_llm_raises_notimplemented():
    # LLM 呼び出し本体は別担当(A/Codex)。未実装はその旨で落ちる。
    from rho.document import Token, Sentence, Document
    s = Sentence("です。", [Token("です","です","助動詞",[],"wago"),
                          Token("。","。","補助記号",["句点"],"kigou")])
    doc = Document(raw="です。", lang="ja", sentences=[s], paragraphs=[[s]])
    try:
        doc.advise()
        assert False, "should raise"
    except NotImplementedError as e:
        assert "advise" in str(e).lower() or "第2段階" in str(e)
