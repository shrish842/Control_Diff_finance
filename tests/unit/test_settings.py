from __future__ import annotations

from controldiff.config import settings


def test_settings_load() -> None:
    assert settings.app_port > 0
    assert settings.database_url
    assert settings.qdrant_collection
