"""build_report の dict を「逸脱の名指し」文へ語り直す純関数。

入力は build_report が返す dict だけ(doc も metrics も見ない)。
語るのは定義が閉じた確定値のみ。近似値(MVR/述語/文/文節/文)には触れない。
逸脱が無い項目はキーごと省く(平凡なら黙る)。
"""


def _narrate_style(report: dict):
    se = report.get("sentence_end")
    if not se:
        return None
    k, j = se.get("keitai", 0), se.get("jotai", 0)
    if k > 0 and j > 0:
        return f"⚠ 敬体と常体が混在(敬体 {k}・常体 {j})"
    if k > 0 and j == 0:
        return f"ほぼ敬体で統一(敬体 {k})"
    if j > 0 and k == 0:
        return f"ほぼ常体で統一(常体 {j})"
    return None


def _narrate_ending(report: dict):
    end = report.get("style_issues", {}).get("ending")
    if not end:
        return None
    streak = end.get("max_streak", {})
    if streak.get("len", 0) >= 3:
        return f"⚠ 同じ語尾「{streak.get('ending','')}」が {streak['len']} 連続"
    top = end.get("top")
    ratio = end.get("top_ratio", 0.0)
    if top and ratio >= 0.4:
        return f"最頻語尾「{top[0]}」が文末の{ratio:.0%}"
    return None


_GOSHU_LABEL = {"kango": "漢語", "wago": "和語", "gairaigo": "外来語"}
_GOSHU_NUANCE = {"wago": "(平仮名寄りのやわらかい文体)", "kango": "(漢語が多く硬い文体)", "gairaigo": ""}


def _narrate_goshu(report: dict):
    g = report.get("goshu")
    if not g:
        return None
    cand = {k: g.get(k, 0.0) for k in _GOSHU_LABEL}
    key = max(cand, key=cand.get)
    ratio = cand[key]
    if ratio <= 0:
        return None
    return f"{_GOSHU_LABEL[key]}{ratio:.0%}{_GOSHU_NUANCE[key]}"


def _narrate_vocabulary(report: dict):
    mtld = report.get("mtld")
    if not mtld:
        return None
    return f"語彙 MTLD {mtld}"


def _narrate_length(report: dict):
    longs = report.get("length", {}).get("long_sentences", [])
    if not longs:
        return None
    return f"⚠ 突出して長い文が {len(longs)} 件"


def narrate(report: dict) -> dict:
    out = {}
    style = _narrate_style(report)
    if style:
        out["style"] = style
    ending = _narrate_ending(report)
    if ending:
        out["ending_repeat"] = ending
    goshu = _narrate_goshu(report)
    if goshu:
        out["goshu"] = goshu
    vocab = _narrate_vocabulary(report)
    if vocab:
        out["vocabulary"] = vocab
    length = _narrate_length(report)
    if length:
        out["length"] = length
    return out
