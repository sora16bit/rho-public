"""文体の癖を「該当文を名指しで」取り出す(AIなしロジック)。

敬体/常体の混在・文末表現の反復と連続・長すぎる文を検出する。
文末辞書は japanese.py のものを再利用する。japanese.py 自体は変更しない。
"""
from collections import Counter
from rho.metrics.japanese import _KEITAI_END, _JOTAI_END


def _ending_style(sentence) -> str:
    """文の文末スタイルを keitai/jotai/other で返す。内容語が無ければ other。"""
    content = sentence.content_tokens()
    if not content:
        return "other"
    last = content[-1].surface
    norm = content[-1].normalized
    if any(last.endswith(e) or norm.endswith(e) for e in _KEITAI_END):
        return "keitai"
    if any(last.endswith(e) or norm.endswith(e) for e in _JOTAI_END):
        return "jotai"
    return "other"


def sentence_style_breakdown(doc) -> dict:
    """敬体/常体/その他に分類し、該当文 text を集める。両方あれば mixed=True。"""
    out = {"keitai": [], "jotai": [], "other": []}
    for s in doc.sentences:
        out[_ending_style(s)].append(s.text)
    out["mixed"] = bool(out["keitai"]) and bool(out["jotai"])
    return out


def _ending_key(sentence, n_chars: int = 4):
    """文末の語尾キー(記号を除いた表層をつなぎ、その末尾 n_chars 文字)。

    最後の内容語(機能語)だけだと「思います」も「します」も「ます」に潰れる。
    末尾の表層文字列で見ることで「思います」「ています」「ましょう」を区別する。
    内容語が無ければ None。
    """
    content = sentence.content_tokens()
    if not content:
        return None
    tail = "".join(t.surface for t in content)
    return tail[-n_chars:] if tail else None


def ending_repetition(doc) -> dict:
    """文末表現の頻度・最頻・最長連続を返す。"""
    keys, texts = [], []
    for s in doc.sentences:
        k = _ending_key(s)
        if k is None:
            continue
        keys.append(k)
        texts.append(s.text)

    total = len(keys)
    counts = Counter(keys)
    if total == 0:
        return {
            "counts": {}, "total": 0, "top": None, "top_ratio": 0.0,
            "max_streak": {"ending": None, "len": 0, "sentences": []},
        }

    ending, count = counts.most_common(1)[0]
    # 最長連続(隣接する同一キー)を走査
    best = {"ending": keys[0], "len": 1, "start": 0}
    cur = {"ending": keys[0], "len": 1, "start": 0}
    for i in range(1, total):
        if keys[i] == keys[i-1]:
            cur["len"] += 1
        else:
            cur = {"ending": keys[i], "len": 1, "start": i}
        if cur["len"] > best["len"]:
            best = dict(cur)
    streak_sents = texts[best["start"]:best["start"] + best["len"]]

    return {
        "counts": dict(counts.most_common()),
        "total": total,
        "top": (ending, count),
        "top_ratio": count / total,
        "max_streak": {
            "ending": best["ending"],
            "len": best["len"],
            "sentences": streak_sents,
        },
    }


def long_sentences(doc, threshold: int = 60) -> list:
    """語数(内容語数)が threshold を超える文を text/words で返す(出現順)。"""
    out = []
    for s in doc.sentences:
        n = len(s.content_tokens())
        if n > threshold:
            out.append({"text": s.text, "words": n})
    return out


def style_issues(doc) -> dict:
    """文体の癖をまとめて返す。"""
    return {
        "style": sentence_style_breakdown(doc),
        "ending": ending_repetition(doc),
        "long": long_sentences(doc),
    }
