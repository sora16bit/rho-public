"""複数の記事を文体の距離で自動グループ分けする(階層クラスタリング)。

使い方:
    .venv/bin/python cluster_rho.py 記事1.txt 記事2.txt 記事3.txt ...
    .venv/bin/python cluster_rho.py -t 2.0 記事1.txt 記事2.txt ...   # threshold 指定

threshold(既定 3.0)より近い記事を同じグループにまとめる。誰も教えなくても、
features の距離だけで「似た文体の記事」が自動でまとまる。データマイニングの華。
"""
import sys
import rho


def main():
    args = sys.argv[1:]
    threshold = 3.0
    if args and args[0] == "-t":
        threshold = float(args[1])
        args = args[2:]
    if not args:
        print("使い方: python cluster_rho.py [-t threshold] 記事1.txt 記事2.txt ...")
        return
    labels = [p.split("/")[-1] for p in args]
    docs = [rho.analyze(open(p, encoding="utf-8").read()) for p in args]
    tree = rho.cluster(docs)
    groups = rho.cut(tree, threshold=threshold)
    print(f"threshold={threshold}(これより近い記事を同じグループに)\n")
    print(rho.format_clusters(groups, labels=labels))


if __name__ == "__main__":
    main()
