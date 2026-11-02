"""Configuration loading: config.yaml validated with Pydantic."""

import os
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel

DEFAULT_CONFIG_PATH = "config.yaml"


class LLMConfig(BaseModel):
    provider: Literal["ollama", "api"] = "ollama"
    model: str = "qwen2.5:7b"
    base_url: str = "http://localhost:11434"


class EmbeddingsConfig(BaseModel):
    model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"


class ChunkingConfig(BaseModel):
    size: int = 400
    overlap: int = 40


class RetrievalConfig(BaseModel):
    k: int = 5


class ScreeningConfig(BaseModel):
    score_threshold: float = 6.0


class PathsConfig(BaseModel):
    profile_dir: Path = Path("data/profile")
    jobs_dir: Path = Path("data/jobs")
    vectorstore_dir: Path = Path("data/vectorstore")
    db_path: Path = Path("data/vagalens.db")


class Settings(BaseModel):
    language: str = "pt-BR"
    llm: LLMConfig = LLMConfig()
    embeddings: EmbeddingsConfig = EmbeddingsConfig()
    chunking: ChunkingConfig = ChunkingConfig()
    retrieval: RetrievalConfig = RetrievalConfig()
    screening: ScreeningConfig = ScreeningConfig()
    paths: PathsConfig = PathsConfig()


def load_config(path: str | Path | None = None) -> Settings:
    """Load settings from `path`, $VAGALENS_CONFIG, or ./config.yaml.

    A missing file falls back to the defaults, so a fresh clone still runs.
    """
    config_path = Path(path or os.environ.get("VAGALENS_CONFIG", DEFAULT_CONFIG_PATH))
    if not config_path.exists():
        return Settings()
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return Settings.model_validate(data)
