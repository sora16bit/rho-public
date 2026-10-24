"""Rho — 文章解析エンジン(第1段階)。

使い方:
    import rho
    doc = rho.analyze("テキスト")   # 文字列から
    doc = rho.load("記事.md")        # ファイルから
    print(doc.report())
"""
from rho.document import Document, Sentence, Token

_analyzer = None

def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        from rho.analyzer.sudachi_ja import SudachiJaAnalyzer
        _analyzer = SudachiJaAnalyzer()
    return _analyzer

def analyze(text: str) -> Document:
    """生テキストを解析して Document を返す。markdown 構造は事前に除去する。"""
    from rho.preprocess import strip_markdown
    return _get_analyzer().analyze(strip_markdown(text))

def load(path: str) -> Document:
    """ファイルを読み込んで解析。内部は文字列を analyze に渡すだけ。"""
    with open(path, encoding="utf-8") as f:
        return analyze(f.read())

from rho.compare import compare, distance
from rho.profile import profile, format_profile
from rho.cluster import cluster, cut, format_clusters

__all__ = ["analyze", "load", "compare", "distance", "profile", "format_profile",
           "cluster", "cut", "format_clusters",
           "Document", "Sentence", "Token"]
