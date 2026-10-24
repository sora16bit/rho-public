"""markdown 構造を除去し本文だけを残す前処理。

統計を歪める非・本文要素(コードブロック・表・見出し行・水平線・
箇条書き/引用マーカー・インラインのリンク/強調)を落とす。
見出しは構造ラベルなので行ごと除去する(本文ではないため統計に混ぜない)。
箇条書き/引用は本文を残しマーカーだけ落とす。Analyzer に渡す前段で使う純関数。
"""
import re

_FENCE = re.compile(r"^[ \t]*(```|~~~).*?$.*?^[ \t]*\1[ \t]*$", re.MULTILINE | re.DOTALL)
_TABLE_ROW = re.compile(r"^[ \t]*\|.*$", re.MULTILINE)
_HRULE = re.compile(r"^[ \t]*([-*_])(?:[ \t]*\1){2,}[ \t]*$", re.MULTILINE)
_HEADING = re.compile(r"^[ \t]*#{1,6}[ \t]+.*$", re.MULTILINE)  # 見出しは行ごと除去
_QUOTE = re.compile(r"^[ \t]*>[ \t]?", re.MULTILINE)
_LIST = re.compile(r"^[ \t]*(?:[-*+]|\d+\.)[ \t]+", re.MULTILINE)
_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_EMPHASIS = re.compile(r"(\*\*|__|\*|_|`)(.+?)\1")
_BLANKS = re.compile(r"\n[ \t]*\n([ \t]*\n)+")

def strip_markdown(text: str) -> str:
    """md 構造を除去して本文を返す。"""
    if not text:
        return text
    # ブロック要素を先に(行単位)
    text = _FENCE.sub("", text)
    text = _TABLE_ROW.sub("", text)
    text = _HRULE.sub("", text)
    text = _HEADING.sub("", text)
    text = _QUOTE.sub("", text)
    text = _LIST.sub("", text)
    # インライン要素
    text = _LINK.sub(r"\1", text)
    text = _EMPHASIS.sub(r"\2", text)
    # 除去で生じた過剰な空行を畳む
    text = _BLANKS.sub("\n\n", text)
    return text
