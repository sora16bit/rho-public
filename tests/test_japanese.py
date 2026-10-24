from rho.document import Token, Sentence, Document

def _doc_from_tokens(tokens):
    s = Sentence("", tokens)
    return Document(raw="", lang="ja", sentences=[s], paragraphs=[[s]])

def test_goshu_ratio():
    from rho.metrics.japanese import goshu_ratio
    doc = _doc_from_tokens([
        Token("国際","国際","名詞",[],"kango"),
        Token("コンピューター","コンピューター","名詞",[],"gairaigo"),
        Token("食べる","食べる","動詞",[],"wago"),
        Token("。","。","補助記号",["句点"],"kigou"),  # 母数から除外
    ])
    r = goshu_ratio(doc)
    assert round(r["kango"], 3) == round(1/3, 3)
    assert round(r["wago"], 3) == round(1/3, 3)
    assert round(r["gairaigo"], 3) == round(1/3, 3)

def test_pos_ratio():
    from rho.metrics.japanese import pos_ratio
    doc = _doc_from_tokens([
        Token("猫","猫","名詞",[],"kango"),
        Token("が","が","助詞",[],"wago"),
        Token("走る","走る","動詞",[],"wago"),
    ])
    r = pos_ratio(doc)
    assert round(r["名詞"], 3) == round(1/3, 3)
    assert round(r["助詞"], 3) == round(1/3, 3)
    assert round(r["動詞"], 3) == round(1/3, 3)

def test_mvr():
    # MVR = (形容詞+副詞+連体詞+接続詞) / 名詞
    from rho.metrics.japanese import mvr
    doc = _doc_from_tokens([
        Token("とても","とても","副詞",[],"wago"),
        Token("美しい","美しい","形容詞",[],"wago"),
        Token("猫","猫","名詞",[],"kango"),
    ])
    assert mvr(doc) == 2.0   # (副詞1+形容詞1)/名詞1

def test_hiragana_ratio_and_chars_per_sentence():
    # 1文。あ(平仮名)5 + 漢(漢字)2 + 字(漢字)3 = 計10文字, 平仮名5。
    from rho.metrics.japanese import hiragana_ratio, chars_per_sentence
    toks = (
        [Token("あ","あ","名詞",[],"wago")]*5 +
        [Token("漢","漢","動詞",[],"kango")]*2 +
        [Token("字","字","名詞",[],"kango")]*3
    )
    doc = _doc_from_tokens(toks)
    assert hiragana_ratio(doc) == 50.0       # 5/10*100
    assert chars_per_sentence(doc) == 10.0   # 10字 / 1文


def test_grade_level_is_retracted():
    # 学年式は撤回済み。合成スコア関数は存在しない。
    import rho.metrics.japanese as J
    assert not hasattr(J, "grade_level")
    assert not hasattr(J, "grade_label")

def test_sentence_end_style():
    from rho.metrics.japanese import sentence_end_style
    doc = Document(raw="", lang="ja", sentences=[
        Sentence("です。", [Token("です","です","助動詞",[],"wago"),
                          Token("。","。","補助記号",["句点"],"kigou")]),
        Sentence("ある。", [Token("ある","ある","動詞",[],"wago"),
                          Token("。","。","補助記号",["句点"],"kigou")]),
    ], paragraphs=[])
    r = sentence_end_style(doc)
    assert r["keitai"] == 1     # です/ます調
    assert r["jotai"] == 1      # だ/である調


def test_hardness_profile_discriminates_easy_from_hard():
    # 合成スコアは撤回したので、生指標が硬さを正しく弁別することを固定する。
    # 設計書(硬)は童話・漱石(易)より 漢語率・名詞率・平均文長 が高いはず。
    import rho
    from rho.metrics.japanese import goshu_ratio, pos_ratio, chars_per_sentence
    youwa  = "むかしむかし、あるところに、おじいさんとおばあさんがいました。"
    soseki = "吾輩は猫である。名前はまだ無い。どこで生れたかとんと見当がつかぬ。"
    katai  = ("本システムは形態素解析の結果をもとにテキストを文節の単位で分割した上で"
              "文の係り受け構造を解析する。複文構造を持つ文字列に対しては係り受け関係を"
              "参照して精度向上を図る。")
    d_you, d_sos, d_kat = rho.analyze(youwa), rho.analyze(soseki), rho.analyze(katai)

    def kango(d):  return goshu_ratio(d)["kango"]
    def noun(d):   return pos_ratio(d).get("名詞", 0.0)

    # 漢語率: 設計書 > 童話・漱石
    assert kango(d_kat) > kango(d_you)
    assert kango(d_kat) > kango(d_sos)
    # 名詞率: 設計書 > 童話・漱石
    assert noun(d_kat) > noun(d_you)
    assert noun(d_kat) > noun(d_sos)
    # 平均文長(字): 設計書 > 漱石
    assert chars_per_sentence(d_kat) > chars_per_sentence(d_sos)
