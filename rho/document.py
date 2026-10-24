"""Rho の一級市民: Document とその構成要素(純データ)。

Document は「何を保持するか」だけを知り、解析方法もメトリクス計算も知らない。
メトリクスは Document を読むだけで、Document 自身は計算しない。
"""
from dataclasses import dataclass, field

SYMBOL_POS = {"補助記号", "記号", "空白"}

@dataclass
class Token:
    surface: str            # 表層形
    normalized: str         # 正規化形(表記ゆれ吸収)
    pos: str                # 品詞大分類
    pos_detail: list        # 品詞細分類
    goshu: str              # 語種 kango/wago/gairaigo/kigou/other

    def is_symbol(self) -> bool:
        return self.pos in SYMBOL_POS

@dataclass
class Sentence:
    text: str
    tokens: list

    def content_tokens(self) -> list:
        """記号を除いた語。"""
        return [t for t in self.tokens if not t.is_symbol()]

@dataclass
class Document:
    raw: str
    lang: str
    sentences: list = field(default_factory=list)
    paragraphs: list = field(default_factory=list)  # list[list[Sentence]]

    def sentence_count(self) -> int:
        return len(self.sentences)

    def paragraph_count(self) -> int:
        return len(self.paragraphs)

    def all_tokens(self) -> list:
        return [t for s in self.sentences for t in s.tokens]

    def content_tokens(self) -> list:
        """記号を除く全語(統計の母数)。"""
        return [t for t in self.all_tokens() if not t.is_symbol()]

    def word_count(self) -> int:
        return len(self.content_tokens())

    # --- 動詞ショートカット(measure系) ---
    def report(self, mode: str = "narrate") -> str:
        from rho.report import format_report
        return format_report(self, mode=mode)

    def report_dict(self) -> dict:
        from rho.report import build_report
        return build_report(self)

    def mtld(self) -> float:
        from rho.metrics.universal import mtld
        return mtld(self)

    def hiragana_ratio(self) -> float:
        from rho.metrics.japanese import hiragana_ratio
        return hiragana_ratio(self)

    def style_issues(self) -> dict:
        from rho.metrics.style import style_issues
        return style_issues(self)

    def long_sentences(self, threshold: int = 60) -> list:
        from rho.metrics.style import long_sentences
        return long_sentences(self, threshold)

    def features(self) -> dict:
        from rho.features import extract_features
        return extract_features(self)

    # --- 動詞ショートカット(read系・第2段階) ---
    def advise(self):
        from rho.advise import advise
        return advise(self)
