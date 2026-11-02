from pathlib import Path

import pytest

from vagalens.config import Settings, load_config

ROOT = Path(__file__).resolve().parents[1]


def test_repo_config_is_valid() -> None:
    settings = load_config(ROOT / "config.yaml")
    assert settings.retrieval.k > 0
    assert settings.chunking.overlap < settings.chunking.size


def test_missing_file_falls_back_to_defaults(tmp_path: Path) -> None:
    assert load_config(tmp_path / "nope.yaml") == Settings()


def test_partial_file_keeps_other_defaults(tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text("retrieval:\n  k: 8\n", encoding="utf-8")
    settings = load_config(cfg)
    assert settings.retrieval.k == 8
    assert settings.llm.model == Settings().llm.model


def test_invalid_provider_is_rejected(tmp_path: Path) -> None:
    cfg = tmp_path / "c.yaml"
    cfg.write_text("llm:\n  provider: nonsense\n", encoding="utf-8")
    with pytest.raises(ValueError):
        load_config(cfg)
