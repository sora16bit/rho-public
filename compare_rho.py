"""2つの文章の構造的特徴を並べて比較する(データマイニングの最小例)。

使い方:
    .venv/bin/python compare_rho.py A.txt B.txt

features() は機械可読な特徴ベクトル。並べると「どこが違う文章か」が
客観的な数値で見える。話題に左右されにくい構造的特徴だけを使う。
"""
import sys
import rho


def main():
    if len(sys.argv) < 3:
        print("使い方: python compare_rho.py A.txt B.txt")
        return
    path_a, path_b = sys.argv[1], sys.argv[2]
    a = rho.analyze(open(path_a, encoding="utf-8").read())
    b = rho.analyze(open(path_b, encoding="utf-8").read())
    fa, fb = a.features(), b.features()

    name_a = path_a.split("/")[-1]
    name_b = path_b.split("/")[-1]
    print(f"{'特徴':24} {name_a:>12} {name_b:>12}  差")
    print("-" * 60)
    for k in fa:
        print(f"{k:24} {fa[k]:>12.3f} {fb[k]:>12.3f}  {fb[k]-fa[k]:+.3f}")

    # 標準化距離(σ単位。率と量を対等に扱う)
    c = rho.compare(a, b)
    print(f"\n総合距離(標準化): {c['distance']}  0に近いほど文体が似ている。")
    print("最も違う特徴トップ3(σ単位):")
    for k, v in c["most_different"]:
        print(f"  {k:24} {v:+.2f}σ")


if __name__ == "__main__":
    main()
