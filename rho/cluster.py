"""複数記事を文体の距離で自動グループ分けする(凝集型 階層クラスタリング)。

cluster() が結合の木(履歴)を返し、cut() が threshold で塊を切り出す。
表示は format_clusters() に分ける(compare/profile と同じ哲学)。

クラスタ間距離は平均連結(average linkage)。外れ値に過敏な単連結より
文体グルーピングに素直。距離そのものは compare.distance に委譲する。
"""

from rho.compare import distance


def distance_matrix(docs: list) -> list:
    """全ペアの標準化距離の N×N 行列(対称・対角 0)。"""
    n = len(docs)
    m = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = distance(docs[i], docs[j])
            m[i][j] = m[j][i] = d
    return m


def cluster(docs: list) -> list:
    """凝集型 階層クラスタリング。結合履歴 [(left, right, dist), ...] を返す。

    left/right は葉 index(0..N-1)または合成ノード id(N 以降)。
    N 本なら N-1 回の結合。1 本なら空、0 本は ValueError。
    """
    n = len(docs)
    if n == 0:
        raise ValueError("cluster() needs at least one document")
    base = distance_matrix(docs)

    # active: ノードid → そのクラスタに属する葉 index 集合
    active = {i: [i] for i in range(n)}
    tree = []
    next_id = n

    def cluster_dist(members_a, members_b):
        """平均連結:両クラスタのメンバー全ペア距離の平均。"""
        total = sum(base[a][b] for a in members_a for b in members_b)
        return total / (len(members_a) * len(members_b))

    while len(active) > 1:
        ids = list(active)
        best = None
        for ai in range(len(ids)):
            for bi in range(ai + 1, len(ids)):
                ia, ib = ids[ai], ids[bi]
                d = cluster_dist(active[ia], active[ib])
                if best is None or d < best[0]:
                    best = (d, ia, ib)
        d, ia, ib = best
        tree.append((ia, ib, d))
        active[next_id] = active[ia] + active[ib]
        del active[ia]
        del active[ib]
        next_id += 1

    return tree


def cut(tree: list, threshold: float) -> list:
    """結合距離が threshold 以下の塊だけを残したグループ分けを返す。

    元 list の index のリストのリスト。例 [[0, 2], [1]]。
    結合距離 > threshold の結合は採用せず、そこで枝を分けたままにする。
    """
    # 葉と合成ノードの所属メンバーを再構成しながら、threshold 以下の結合だけ採用。
    if not tree:
        return [[0]]  # 1 本(結合なし)。葉 0 が単独グループ。

    n = len(tree) + 1  # 葉の数(N-1 回の結合 → N 葉)
    members = {i: [i] for i in range(n)}
    groups = {i: [i] for i in range(n)}  # 現在のグループ集合(id → 葉 index)
    next_id = n
    for left, right, d in tree:
        merged = members[left] + members[right]
        members[next_id] = merged
        if d <= threshold:
            groups[next_id] = merged
            del groups[left]
            del groups[right]
        next_id += 1

    return [sorted(g) for g in groups.values()]


def format_clusters(groups: list, labels: list = None) -> str:
    """グループ分けを人間向けに整形する。各グループの記事名を列挙。"""
    labels = labels or [f"#{i}" for i in range(sum(len(g) for g in groups))]
    lines = []
    for n, group in enumerate(sorted(groups, key=lambda g: min(g)), start=1):
        names = "、".join(str(labels[i]) for i in sorted(group))
        lines.append(f"グループ{n}({len(group)}本): {names}")
    return "\n".join(lines)
