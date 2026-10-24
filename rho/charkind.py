"""字種判定と語種(漢語/和語/外来語)の近似推定。

語種は SudachiPy の品詞に無いため、表層の字種構成から近似する。
第1段階の近似であり、精度向上は第2段階(語種辞書導入)で行う。
"""

def char_kind(ch: str) -> str:
    """1文字の字種を返す: kanji/hiragana/katakana/other。"""
    code = ord(ch)
    if 0x3040 <= code <= 0x309F:
        return "hiragana"
    if 0x30A0 <= code <= 0x30FF or code == 0x30FC:  # カタカナ + 長音符
        return "katakana"
    if 0x4E00 <= code <= 0x9FFF or 0x3400 <= code <= 0x4DBF:
        return "kanji"
    return "other"

def word_goshu(surface: str, reading: str) -> str:
    """語の語種を近似推定: kango/wago/gairaigo/kigou/other。

    規則(優先順):
    - 記号のみ → kigou
    - カタカナを含み漢字・ひらがなを含まない → gairaigo(外来語)
    - 漢字を含み ひらがな(送り仮名)を含まない → kango(漢語)
    - ひらがなを含む(送り仮名がある活用語や和語) → wago(和語)
    - それ以外 → other
    """
    kinds = [char_kind(c) for c in surface if not c.isspace()]
    if not kinds:
        return "other"
    has_kanji = "kanji" in kinds
    has_hira = "hiragana" in kinds
    has_kata = "katakana" in kinds
    non_other = [k for k in kinds if k != "other"]
    if not non_other:  # 句読点・記号・英数のみ
        return "kigou"
    if has_kata and not has_kanji and not has_hira:
        return "gairaigo"
    if has_kanji and not has_hira:
        return "kango"
    if has_hira:
        return "wago"
    return "other"
