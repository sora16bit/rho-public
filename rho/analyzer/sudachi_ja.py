"""SudachiPy による日本語 Analyzer。

文分割: 句点「。」「！」「？」で区切る(記号は直前文に含める)。
段落分割: 空行(連続改行)で区切る。
分割モード: C(最長単位)。
"""
import re
from sudachipy import dictionary, tokenizer
from rho.analyzer.base import Analyzer
from rho.document import Token, Sentence, Document
from rho.charkind import word_goshu

_SENT_END = "。！？!?"

class SudachiJaAnalyzer(Analyzer):
    lang = "ja"

    def __init__(self):
        self._tok = dictionary.Dictionary().create()
        self._mode = tokenizer.Tokenizer.SplitMode.C

    def _split_sentences(self, para: str) -> list:
        # 文末記号の直後で区切る。記号は前の文に残す。
        out, buf = [], ""
        for ch in para:
            buf += ch
            if ch in _SENT_END:
                out.append(buf.strip())
                buf = ""
        if buf.strip():
            out.append(buf.strip())
        return [s for s in out if s]

    def _to_tokens(self, sent_text: str) -> list:
        toks = []
        for m in self._tok.tokenize(sent_text, self._mode):
            pos = m.part_of_speech()
            toks.append(Token(
                surface=m.surface(),
                normalized=m.normalized_form(),
                pos=pos[0],
                pos_detail=[p for p in pos[1:] if p != "*"],
                goshu=word_goshu(m.surface(), m.reading_form()),
            ))
        return toks

    def analyze(self, text: str) -> Document:
        paragraphs, sentences = [], []
        raw_paras = re.split(r"\n\s*\n", text.strip()) if text.strip() else []
        for rp in raw_paras:
            rp = rp.strip()
            if not rp:
                continue
            para_sents = []
            for st in self._split_sentences(rp):
                s = Sentence(text=st, tokens=self._to_tokens(st))
                para_sents.append(s)
                sentences.append(s)
            if para_sents:
                paragraphs.append(para_sents)
        return Document(raw=text, lang="ja",
                        sentences=sentences, paragraphs=paragraphs)
