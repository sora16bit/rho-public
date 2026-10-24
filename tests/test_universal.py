import math
from rho.document import Token, Sentence, Document

def _doc(sentences):
    sents = []
    for words in sentences:
        toks = [Token(w, w, "名詞", [], "wago") for w in words]
        toks.append(Token("。","。","補助記号",["句点"],"kigou"))
        sents.append(Sentence("".join(words)+"。", toks))
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])

def test_basic_counts():
    from rho.metrics.universal import basic_counts
    doc = _doc([["猫","だ"], ["犬","だ","よ"]])
    r = basic_counts(doc)
    assert r["sentences"] == 2
    assert r["words"] == 5          # 記号を除く
    assert r["avg_sentence_length"] == 2.5

def test_length_distribution_flags_long():
    from rho.metrics.universal import length_distribution
    short = _doc([["あ","い"]])           # 2語
    r = length_distribution(short, long_threshold=10)
    assert r["max"] == 2
    assert r["long_sentences"] == []

def test_mtld_diverse_higher_than_repetitive():
    from rho.metrics.universal import mtld
    diverse = Document(raw="", lang="ja", sentences=[
        Sentence("", [Token(w, w, "名詞", [], "wago")
                      for w in ["猫","犬","鳥","魚","象","虎","熊","鹿","馬","牛"]])
    ])
    repetitive = Document(raw="", lang="ja", sentences=[
        Sentence("", [Token("猫","猫","名詞",[],"wago") for _ in range(10)])
    ])
    assert mtld(diverse) > mtld(repetitive)

def test_mtld_empty_is_zero():
    from rho.metrics.universal import mtld
    doc = Document(raw="", lang="ja", sentences=[])
    assert mtld(doc) == 0.0
