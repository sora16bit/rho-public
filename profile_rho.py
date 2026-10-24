"""複数の文章を一覧表にして傾向を俯瞰する(compare の N 本版)。

使い方:
    .venv/bin/python profile_rho.py 記事1.txt 記事2.txt 記事3.txt ...

自分の全記事を並べると「この1本だけ文長が長い」「常体率がばらついている」が
一目で分かる。各列の最下部に mean / std を出す。数字は比較対象があって初めて意味が出る。
"""
import sys
import rho


def main():
    if len(sys.argv) < 2:
        print("使い方: python profile_rho.py 記事1.txt 記事2.txt ...")
        return
    paths = sys.argv[1:]
    docs = [rho.analyze(open(p, encoding="utf-8").read()) for p in paths]
    labels = [p.split("/")[-1] for p in paths]
    print(rho.format_profile(rho.profile(docs), labels=labels))


if __name__ == "__main__":
    main()
