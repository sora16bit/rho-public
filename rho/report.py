"""全メトリクスを集約し、辞書化・整形表示する。計算は metrics に委譲。"""
from rho.metrics import universal as U
from rho.metrics import japanese as J
from rho.metrics import style as S

def build_report(doc) -> dict:
    """メトリクスを1つの辞書に束ねる。各計算は隔離し失敗を局所化。"""
    out = {}
    def safe(name, fn):
        try:
            out[name] = fn(doc)
        except Exception as e:  # 1指標の失敗が全体を壊さない
            out[name] = {"error": str(e)}
    safe("basic", U.basic_counts)
    safe("length", U.length_distribution)
    out["mtld"] = U.mtld(doc)
    if doc.lang == "ja":
        out["goshu"] = J.goshu_ratio(doc)
        out["pos"] = J.pos_ratio(doc)
        out["predicates_per_sentence"] = J.predicates_per_sentence(doc)
        out["bunsetsu_per_sentence"] = J.bunsetsu_per_sentence(doc)
        out["mvr"] = J.mvr(doc)
        out["hardness"] = {
            "kango_ratio": out["goshu"]["kango"],
            "hiragana_ratio": J.hiragana_ratio(doc),
            "chars_per_sentence": round(J.chars_per_sentence(doc), 1),
            "noun_ratio": out["pos"].get("名詞", 0.0),
            "mtld": out["mtld"],
        }
        out["style_issues"] = S.style_issues(doc)
        out["sentence_end"] = J.sentence_end_style(doc)
    return out

def format_report(doc, mode: str = "narrate") -> str:
    if mode == "raw":
        return _format_raw(doc)
    return _format_narrate(doc)


def _format_narrate(doc) -> str:
    from rho.narrate import narrate
    r = build_report(doc)
    b = r["basic"]
    lines = ["=" * 40, "  Rho 文章解析レポート", "=" * 40]
    lines.append(f"文数: {b['sentences']}　段落数: {b['paragraphs']}　"
                 f"語数: {b['words']}　文字数: {b['chars']}")
    n = narrate(r)
    order = ["style", "ending_repeat", "goshu", "vocabulary", "length"]
    said = [n[k] for k in order if k in n]
    if said:
        lines.append("― 文章の特徴 ―")
        lines.extend("  " + s for s in said)
    else:
        lines.append("  目立った偏りは見られません。")
    lines.append("=" * 40)
    return "\n".join(lines)


def _format_raw(doc) -> str:
    r = build_report(doc)
    b = r["basic"]
    lines = []
    lines.append("=" * 40)
    lines.append("  Rho 文章解析レポート")
    lines.append("=" * 40)
    lines.append(f"文数: {b['sentences']}　段落数: {b['paragraphs']}　"
                 f"語数: {b['words']}　文字数: {b['chars']}")
    lines.append(f"平均文長: {b['avg_sentence_length']} 語/文")
    lng = r["length"]
    lines.append(f"最長文: {lng['max']} 語　最短文: {lng['min']} 語")
    if lng["long_sentences"]:
        lines.append(f"⚠ 長すぎる文 {len(lng['long_sentences'])} 件（読みにくさの要因）")
    lines.append(f"語彙の豊かさ MTLD: {r['mtld']}")
    if doc.lang == "ja":
        g = r["goshu"]
        lines.append(f"語種比率 — 漢語 {g['kango']:.0%}／和語 {g['wago']:.0%}／"
                     f"外来語 {g['gairaigo']:.0%}")
        lines.append(f"MVR(文体の動的さ): {r['mvr']}")
        lines.append(f"述語/文: {r['predicates_per_sentence']}　"
                     f"文節/文: {r['bunsetsu_per_sentence']}")
        h = r["hardness"]
        lines.append("― 硬さプロファイル(高い=硬い) ―")
        lines.append(f"  漢語率 {h['kango_ratio']:.0%}／平仮名率 {h['hiragana_ratio']:.0f}%／"
                     f"名詞率 {h['noun_ratio']:.0%}")
        lines.append(f"  平均文長 {h['chars_per_sentence']} 字/文／語彙の多様さ MTLD {h['mtld']}")
        si = r["style_issues"]
        st, en, lg = si["style"], si["ending"], si["long"]
        prof = []
        if st["mixed"]:
            prof.append(f"敬体/常体が混在(敬体 {len(st['keitai'])}・常体 {len(st['jotai'])})")
        if en["top"]:
            prof.append(f"語尾「{en['top'][0]}」が最頻({en['top'][1]}回/全文末の{en['top_ratio']:.0%})")
        if prof:
            lines.append("― 文体の癖 ―")
            lines.append("  " + "。".join(prof) + "。")
            if en["max_streak"]["len"] >= 3:
                lines.append(f"  ⚠ 同じ語尾が {en['max_streak']['len']} 連続する箇所あり")
            if lg:
                lines.append(f"  ⚠ 長すぎる文 {len(lg)} 件（Python: doc.long_sentences()）")
        se = r["sentence_end"]
        lines.append(f"文末 — 敬体 {se['keitai']}／常体 {se['jotai']}／その他 {se['other']}")
        if se["keitai"] > 0 and se["jotai"] > 0:
            lines.append("⚠ 敬体と常体が混在しています")
    lines.append("=" * 40)
    return "\n".join(lines)
