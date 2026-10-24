"""第2段階(AI講評)の地ならし。

`doc.advise()` は LLM(Claude)に文章を講評させる「読む動詞」。
LLM 呼び出し本体は別担当(A)が実装する。ここでは LLM に渡す材料を
1つの dict にまとめる `build_context` だけを用意する(LLM は呼ばない)。

設計の芯: 第1段階(measure)が出した数字と該当文を、そのまま LLM の
入力に流し込める形に整える。advise はその context を使ってプロンプトを
組み Claude を呼ぶ — その部分は build_context の上に後付けする。
"""


def build_context(doc) -> dict:
    """LLM 講評に渡す材料を1つの dict にまとめる(純データ・LLM 非依存)。

    返り値:
        {
          "text":    原文,
          "lang":    言語コード,
          "metrics": report_dict()(硬さプロファイル・文体の癖・基礎統計を含む),
        }
    """
    return {
        "text": doc.raw,
        "lang": doc.lang,
        "metrics": doc.report_dict(),
    }


def advise(doc):
    """文章を LLM に講評させる(第2段階)。本体は未実装。

    build_context(doc) で材料は揃う。LLM 呼び出しは別担当(A)が
    この関数の中身として実装する。
    """
    raise NotImplementedError(
        "advise() は第2段階(AI講評)で実装予定。"
        "材料は rho.advise.build_context(doc) で取得できる。"
    )
