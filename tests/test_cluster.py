"""cluster() / cut() / format_clusters() のテスト。

距離は compare.distance に委譲するので、ここでは凝集ロジック(距離行列・結合の木・
threshold での cut)の正しさを、SudachiPy なしで組める最小 Document で検証する。
"""
import pytest

from rho.document import Token, Sentence, Document


def _doc(sentences):
    sents = [Sentence(t, toks) for t, toks in sentences]
    return Document(raw="", lang="ja", sentences=sents, paragraphs=[sents])


def _soft(extra=""):
    """常体・短文・和語多めのやわらかい文書。"""
    return _doc([
        ("猫が走る。", [Token("猫", "猫", "名詞", [], "wago"),
                     Token("が", "が", "助詞", [], "wago"),
                     Token("走る", "走る", "動詞", [], "wago"),
                     Token("。", "。", "補助記号", ["句点"], "kigou")]),
    ])


def _hard():
    """漢語・名詞多め・読点多めの硬い文書。"""
    return _doc([
        ("形態素解析を実行する、構造を解析する。", [
            Token("形態素", "形態素", "名詞", [], "kango"),
            Token("解析", "解析", "名詞", [], "kango"),
            Token("を", "を", "助詞", [], "wago"),
            Token("実行", "実行", "名詞", [], "kango"),
            Token("する", "する", "動詞", [], "wago"),
            Token("、", "、", "補助記号", ["読点"], "kigou"),
            Token("構造", "構造", "名詞", [], "kango"),
            Token("を", "を", "助詞", [], "wago"),
            Token("解析", "解析", "名詞", [], "kango"),
            Token("する", "する", "動詞", [], "wago"),
            Token("。", "。", "補助記号", ["句点"], "kigou")]),
    ])


# --- 距離行列 ---

def test_distance_matrix_symmetric_zero_diagonal():
    from rho.cluster import distance_matrix
    docs = [_soft(), _hard(), _soft()]
    m = distance_matrix(docs)
    n = len(docs)
    for i in range(n):
        assert m[i][i] == 0.0
        for j in range(n):
            assert m[i][j] == m[j][i]


# --- cluster()(結合の木) ---

def test_cluster_returns_n_minus_1_merges():
    from rho.cluster import cluster
    docs = [_soft(), _hard(), _soft(), _hard()]
    tree = cluster(docs)
    assert len(tree) == len(docs) - 1


def test_single_doc_tree_is_empty():
    from rho.cluster import cluster
    assert cluster([_soft()]) == []


def test_empty_raises():
    from rho.cluster import cluster
    with pytest.raises(ValueError):
        cluster([])


# --- cut()(threshold でグループ分け) ---

def test_cut_separates_soft_and_hard():
    from rho.cluster import cluster, cut
    # 0,2 = soft / 1,3 = hard。低 threshold で soft 同士・hard 同士が同じグループ。
    docs = [_soft(), _hard(), _soft(), _hard()]
    tree = cluster(docs)
    groups = cut(tree, threshold=1.0)
    sets = {frozenset(g) for g in groups}
    assert frozenset([0, 2]) in sets   # soft 2本が同じグループ
    assert frozenset([1, 3]) in sets   # hard 2本が同じグループ


def test_cut_high_threshold_merges_all():
    from rho.cluster import cluster, cut
    docs = [_soft(), _hard(), _soft(), _hard()]
    tree = cluster(docs)
    groups = cut(tree, threshold=1e9)
    assert len(groups) == 1
    assert sorted(groups[0]) == [0, 1, 2, 3]


def test_cut_single_doc():
    from rho.cluster import cluster, cut
    tree = cluster([_soft()])
    assert cut(tree, threshold=1.0) == [[0]]


# --- format_clusters ---

def test_format_clusters_contains_groups_and_labels():
    from rho.cluster import format_clusters
    text = format_clusters([[0, 2], [1]], labels=["A.md", "B.md", "C.md"])
    assert "A.md" in text and "B.md" in text and "C.md" in text
