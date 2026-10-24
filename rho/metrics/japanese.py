"""日本語パック: 語種率/品詞率/述語数/文節数/MVR/推奨学年/文末表現。

語種・文節は SudachiPy に無いため近似(charkind / 自立語数)。
推奨学年(grade_level)は 柴崎・沢井(2007) / 李ら NLP2009 の重回帰式
(平仮名率・述語数・文字数・文節数)の係数をそのまま使用。
"""
from collections import Counter
from rho.charkind import char_kind

JIRITSU_POS = {"名詞","動詞","形容詞","副詞","連体詞","接続詞","感動詞","代名詞"}
PREDICATE_POS = {"動詞","形容詞","形状詞"}

def _content(doc):
    return doc.content_tokens()

def goshu_ratio(doc) -> dict:
    toks = _content(doc)
    n = len(toks)
    if n == 0:
        return {"kango": 0.0, "wago": 0.0, "gairaigo": 0.0, "other": 0.0}
    c = Counter(t.goshu for t in toks)
    return {k: c.get(k, 0) / n for k in ("kango", "wago", "gairaigo", "other")}

def pos_ratio(doc) -> dict:
    toks = [t for t in doc.all_tokens() if not t.is_symbol()]
    n = len(toks)
    if n == 0:
        return {}
    c = Counter(t.pos for t in toks)
    return {pos: cnt / n for pos, cnt in c.items()}

def mvr(doc) -> float:
    """MVR = (形容詞+副詞+連体詞+接続詞) / 名詞。名詞0なら0.0。"""
    toks = _content(doc)
    c = Counter(t.pos for t in toks)
    v = c.get("形容詞",0)+c.get("副詞",0)+c.get("連体詞",0)+c.get("接続詞",0)
    nouns = c.get("名詞",0)
    return round(v / nouns, 3) if nouns else 0.0

def predicates_per_sentence(doc) -> float:
    """1文あたり平均述語数(動詞・形容詞・形状詞)。"""
    if not doc.sentences:
        return 0.0
    total = sum(1 for t in doc.content_tokens() if t.pos in PREDICATE_POS)
    return round(total / doc.sentence_count(), 3)

def bunsetsu_per_sentence(doc) -> float:
    """1文あたり平均文節数(自立語数で近似)。"""
    if not doc.sentences:
        return 0.0
    total = sum(1 for t in doc.content_tokens() if t.pos in JIRITSU_POS)
    return round(total / doc.sentence_count(), 3)

def _content_chars(doc) -> str:
    """記号・空白を除いた全文字を連結して返す(文字数・字種カウント用)。"""
    out = []
    for t in doc.content_tokens():
        for ch in t.surface:
            if not ch.isspace():
                out.append(ch)
    return "".join(out)

def hiragana_ratio(doc) -> float:
    """記号・空白を除いた全文字に占める平仮名の割合(百分率 0〜100)。"""
    chars = _content_chars(doc)
    if not chars:
        return 0.0
    hira = sum(1 for c in chars if char_kind(c) == "hiragana")
    return hira / len(chars) * 100

def chars_per_sentence(doc) -> float:
    """1文あたり平均文字数(記号・空白を除く)。"""
    if not doc.sentences:
        return 0.0
    return len(_content_chars(doc)) / doc.sentence_count()

# 注: 単一の可読性/学年スコアは撤回した。NLP2009学年式は CaboCha 係り受け解析
# を前提とし、形態素近似ではサ変名詞を述語に数えず複合名詞を文節と過剰カウント
# するため、硬い技術文で難易度の順序が逆転した(設計 2026-06-14 改訂参照)。
# 代わりに report 側で生指標(漢語率/平仮名率/平均文長/名詞率/MTLD)を並べる
# 「硬さプロファイル」として提示する。学年推定は第2段階(GiNZA導入後)の課題。

_KEITAI_END = ("です","ます","ました","ません","でしょう","ましょう")
_JOTAI_END  = ("だ","である","だった","た","る","ない","い")

def sentence_end_style(doc) -> dict:
    """文末表現で 敬体/常体 を分類(文末辞書による近似)。"""
    keitai = jotai = other = 0
    for s in doc.sentences:
        content = [t for t in s.tokens if not t.is_symbol()]
        if not content:
            continue
        last = content[-1].surface
        norm = content[-1].normalized
        if any(last.endswith(e) or norm.endswith(e) for e in _KEITAI_END):
            keitai += 1
        elif any(last.endswith(e) or norm.endswith(e) for e in _JOTAI_END):
            jotai += 1
        else:
            other += 1
    return {"keitai": keitai, "jotai": jotai, "other": other}
