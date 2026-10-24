from rho.analyzer.sudachi_ja import SudachiJaAnalyzer
from rho.report import build_report, format_report

def test_build_report_has_sections():
    doc = SudachiJaAnalyzer().analyze(
        "吾輩は猫である。名前はまだ無い。どこで生まれたか見当もつかぬ。")
    r = build_report(doc)
    assert "basic" in r
    assert "mtld" in r
    assert "hardness" in r
    for k in ("kango_ratio", "hiragana_ratio", "chars_per_sentence",
              "noun_ratio", "mtld"):
        assert k in r["hardness"]
    assert "goshu" in r
    assert "style_issues" in r
    assert "style" in r["style_issues"]
    assert r["basic"]["sentences"] == 3

def test_format_report_is_string():
    # raw モードは従来の生数値表(硬さプロファイル付き)
    doc = SudachiJaAnalyzer().analyze("猫である。犬もいる。")
    text = format_report(doc, mode="raw")
    assert isinstance(text, str)
    assert "文数" in text
    assert "硬さプロファイル" in text
    # 文体の癖セクションが出る(敬体/常体の語がある文書)
    doc2 = SudachiJaAnalyzer().analyze("私は思います。それは良いと思います。良いね。")
    text2 = format_report(doc2, mode="raw")
    assert "文体の癖" in text2


import rho


def _doc():
    return rho.analyze("これはテストです。私は思います。それは良いと思います。走る。")


def test_raw_mode_matches_legacy_table():
    out = format_report(_doc(), mode="raw")
    assert "Rho 文章解析レポート" in out
    assert "MVR(文体の動的さ)" in out      # raw には近似値が残る
    assert "述語/文" in out


def test_default_mode_is_narrate():
    out = format_report(_doc())
    # narrate は近似値ラベルを出さない
    assert "MVR(文体の動的さ)" not in out
    assert "述語/文" not in out


def test_narrate_shows_deviation():
    out = format_report(_doc(), mode="narrate")
    assert "混在" in out          # 敬体3・常体1 の混在を名指し


def test_doc_report_mode_passthrough():
    assert "MVR" in _doc().report(mode="raw")
    assert "MVR" not in _doc().report()


from rho.cli import main


def test_cli_default_is_narrate(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("これはテストです。私は思います。それは良いと思います。走る。", encoding="utf-8")
    main(["analyze", str(f)])
    out = capsys.readouterr().out
    assert "MVR" not in out


def test_cli_raw_flag(tmp_path, capsys):
    f = tmp_path / "a.txt"
    f.write_text("これはテストです。私は思います。それは良いと思います。走る。", encoding="utf-8")
    main(["analyze", str(f), "--raw"])
    out = capsys.readouterr().out
    assert "MVR" in out
