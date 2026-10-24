"""calibrate_scale.py(FEATURE_SCALE 算出ツール)のテスト。

scripts/ はパッケージではないので、importlib でファイルから直接ロードする。
σ 計算ロジックだけを検証する(ファイル I/O や rho.analyze は CLI ラッパに隔離)。
"""
import importlib.util
from pathlib import Path

import pytest

from rho.compare import FEATURE_SCALE

_PATH = Path(__file__).resolve().parent.parent / "scripts" / "calibrate_scale.py"


def _load():
    spec = importlib.util.spec_from_file_location("calibrate_scale", _PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _full(**overrides):
    feats = {k: 0.0 for k in FEATURE_SCALE}
    feats.update(overrides)
    return feats


# --- compute_scale ---

def test_compute_scale_matches_population_sigma():
    cal = _load()
    # kango_ratio = 0.1, 0.2, 0.3 → 母σ = 0.081649658
    rows = [_full(kango_ratio=0.1), _full(kango_ratio=0.2), _full(kango_ratio=0.3)]
    scale = cal.compute_scale(rows)
    assert scale["kango_ratio"] == pytest.approx(0.081649658)


def test_compute_scale_single_row_all_zero():
    cal = _load()
    scale = cal.compute_scale([_full(kango_ratio=0.42)])
    assert all(v == 0.0 for v in scale.values())


def test_compute_scale_covers_all_features():
    cal = _load()
    scale = cal.compute_scale([_full(), _full()])
    assert set(scale.keys()) == set(FEATURE_SCALE.keys())


# --- warnings_for ---

def test_warns_when_fewer_than_three():
    cal = _load()
    rows = [_full(kango_ratio=0.1), _full(kango_ratio=0.2)]
    warnings = cal.warnings_for(rows, cal.compute_scale(rows))
    assert any("2" in w and "本" in w for w in warnings)


def test_warns_naming_zero_sigma_feature():
    cal = _load()
    # 3本だが gairaigo_ratio は全部同値 → σ=0
    rows = [_full(kango_ratio=0.1), _full(kango_ratio=0.2), _full(kango_ratio=0.3)]
    scale = cal.compute_scale(rows)
    warnings = cal.warnings_for(rows, scale)
    assert any("gairaigo_ratio" in w for w in warnings)


def test_no_warnings_when_healthy():
    cal = _load()
    # 5本・全特徴ばらつきあり → 警告なし
    rows = [
        {k: 0.1 + 0.05 * j for k in FEATURE_SCALE}
        for j in range(5)
    ]
    warnings = cal.warnings_for(rows, cal.compute_scale(rows))
    assert warnings == []


# --- format_scale ---

def test_format_scale_is_pastable():
    cal = _load()
    scale = cal.compute_scale([_full(kango_ratio=0.1), _full(kango_ratio=0.3)])
    text = cal.format_scale(scale)
    assert "FEATURE_SCALE = {" in text
    assert "kango_ratio" in text
