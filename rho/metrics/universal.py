"""言語非依存メトリクス: 基礎カウント / 文長分布 / MTLD。"""

def basic_counts(doc) -> dict:
    sent_lens = [len(s.content_tokens()) for s in doc.sentences]
    words = sum(sent_lens)
    avg = round(words / len(sent_lens), 2) if sent_lens else 0.0
    return {
        "sentences": doc.sentence_count(),
        "paragraphs": doc.paragraph_count(),
        "words": words,
        "chars": len(doc.raw),
        "avg_sentence_length": avg,
    }

def length_distribution(doc, long_threshold: int = 60) -> dict:
    """文ごとの語数分布。long_threshold 超えの文を長文として列挙。"""
    lens = [len(s.content_tokens()) for s in doc.sentences]
    longs = [{"index": i, "length": n, "text": doc.sentences[i].text}
             for i, n in enumerate(lens) if n > long_threshold]
    return {
        "lengths": lens,
        "max": max(lens) if lens else 0,
        "min": min(lens) if lens else 0,
        "long_sentences": longs,
    }

def _ttr_factor_count(words: list, threshold: float = 0.720) -> float:
    """MTLD の片方向ファクター数。McCarthy & Jarvis (2010)。"""
    if not words:
        return 0.0
    factors = 0.0
    types = set()
    token_count = 0
    for w in words:
        token_count += 1
        types.add(w)
        ttr = len(types) / token_count
        if ttr <= threshold:
            factors += 1
            types.clear()
            token_count = 0
    # 端数(未完ファクター)を補完
    if token_count > 0:
        ttr = len(types) / token_count
        ifc = (1 - ttr) / (1 - threshold) if (1 - threshold) else 0
        factors += ifc
    return factors

def mtld(doc, threshold: float = 0.720) -> float:
    """語彙多様性 MTLD。双方向(左→右・右→左)の平均長を平均する。"""
    words = [t.normalized for t in doc.content_tokens()]
    if len(words) < 2:
        return 0.0
    fwd = _ttr_factor_count(words, threshold)
    bwd = _ttr_factor_count(list(reversed(words)), threshold)
    n = len(words)
    fwd_mtld = n / fwd if fwd else n
    bwd_mtld = n / bwd if bwd else n
    return round((fwd_mtld + bwd_mtld) / 2, 2)
