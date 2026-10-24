from rho.narrate import narrate


def _mixed_report():
    return {
        "sentence_end": {"keitai": 3, "jotai": 1, "other": 0},
        "style_issues": {
            "ending": {"top": ("思います", 2), "top_ratio": 0.5, "total": 4,
                       "max_streak": {"ending": "思います", "len": 2, "sentences": []},
                       "counts": {"思います": 2}},
            "style": {"keitai": [], "jotai": [], "other": [], "mixed": True},
            "long": [],
        },
        "goshu": {"kango": 0.2, "wago": 0.7, "gairaigo": 0.04, "other": 0.06},
        "mtld": 51.4,
        "length": {"long_sentences": []},
    }


def test_style_mixed_is_warned():
    out = narrate(_mixed_report())
    assert "混在" in out["style"]
    assert "敬体 3" in out["style"] and "常体 1" in out["style"]


def test_style_unified_when_one_is_zero():
    r = _mixed_report()
    r["sentence_end"] = {"keitai": 0, "jotai": 84, "other": 0}
    out = narrate(r)
    assert "統一" in out["style"]
    assert "混在" not in out["style"]


def test_ending_streak_warned_when_ge_3():
    r = _mixed_report()
    r["style_issues"]["ending"]["max_streak"] = {"ending": "だ", "len": 3, "sentences": []}
    out = narrate(r)
    assert "3" in out["ending_repeat"] and "連続" in out["ending_repeat"]


def test_ending_top_ratio_named_with_percent():
    out = narrate(_mixed_report())
    assert "思います" in out["ending_repeat"] and "50%" in out["ending_repeat"]


def test_goshu_names_max_with_number():
    out = narrate(_mixed_report())  # wago 0.7 が最大
    assert "和語" in out["goshu"] and "70%" in out["goshu"]


def test_mtld_is_number_only_no_judgement():
    out = narrate(_mixed_report())
    assert "51.4" in out["vocabulary"]
    assert "多様" not in out["vocabulary"] and "単調" not in out["vocabulary"]


def test_long_sentences_warned_when_present():
    r = _mixed_report()
    r["length"]["long_sentences"] = ["とても長い文1", "とても長い文2"]
    out = narrate(r)
    assert "長い文" in out["length"] and "2" in out["length"]


def test_long_sentences_silent_when_none():
    out = narrate(_mixed_report())  # long_sentences = []
    assert "length" not in out


def test_approx_metrics_never_appear():
    out = narrate(_mixed_report())
    blob = " ".join(out.values())
    for word in ("MVR", "述語", "文節"):
        assert word not in blob
    assert "mvr" not in out and "predicates_per_sentence" not in out \
        and "bunsetsu_per_sentence" not in out


def test_silent_when_plain():
    plain = {
        "sentence_end": {"keitai": 0, "jotai": 0, "other": 0},
        "style_issues": {"ending": {"top": None, "top_ratio": 0.0, "total": 0,
                                    "max_streak": {"ending": "", "len": 0, "sentences": []},
                                    "counts": {}},
                         "style": {"keitai": [], "jotai": [], "other": [], "mixed": False},
                         "long": []},
        "goshu": {"kango": 0.0, "wago": 0.0, "gairaigo": 0.0, "other": 0.0},
        "mtld": 0.0,
        "length": {"long_sentences": []},
    }
    out = narrate(plain)
    assert "style" not in out and "ending_repeat" not in out and "length" not in out
