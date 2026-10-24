"""Analyzer 抽象基底: 生テキスト → 充填済み Document。

解析器を差し替え可能にする境界。メトリクスもファイルも知らない。
"""
from abc import ABC, abstractmethod
from rho.document import Document

class Analyzer(ABC):
    lang: str = ""

    @abstractmethod
    def analyze(self, text: str) -> Document:
        ...
