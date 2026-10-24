"""Rho を Python から使うサンプル。

使い方:
    .venv/bin/python try_rho.py 記事.txt
    .venv/bin/python try_rho.py            # 引数なしなら下のSAMPLEを解析

自分の note/X の文章を .txt に貼って渡せば、文体の癖を該当文付きで出す。
"""
import sys
import rho

SAMPLE = "ここに文章を貼ってもいい。私は思います。それは良いと思います。良いね。"


def main():
    if len(sys.argv) > 1:
        text = open(sys.argv[1], encoding="utf-8").read()
    else:
        text = SAMPLE

    doc = rho.analyze(text)

    # --- 1. レポート全文(硬さプロファイル + 文体の癖) ---
    print(doc.report())
    print()

    # --- 2. 文体の癖を該当文付きで引く ---
    si = doc.style_issues()

    print("◆ 文末表現トップ5")
    for ending, cnt in list(si["ending"]["counts"].items())[:5]:
        pct = cnt / si["ending"]["total"] * 100
        print(f"  「{ending}」{cnt}回 ({pct:.0f}%)")

    streak = si["ending"]["max_streak"]
    if streak["len"] >= 2:
        print(f"\n◆ 「{streak['ending']}」が{streak['len']}連続する箇所")
        for s in streak["sentences"]:
            print(f"  ・{s}")

    if si["style"]["mixed"]:
        print(f"\n◆ 常体の文(敬体の中で浮く候補・最大10件)")
        for s in si["style"]["jotai"][:10]:
            print(f"  ・{s}")

    longs = doc.long_sentences(threshold=30)   # ← この数字を触ると感度が変わる
    if longs:
        print(f"\n◆ 長すぎる文(30語超)")
        for x in longs:
            print(f"  ({x['words']}語) {x['text']}")


if __name__ == "__main__":
    main()
