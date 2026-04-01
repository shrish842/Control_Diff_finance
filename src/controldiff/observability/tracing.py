from __future__ import annotations

import logging

from controldiff.config import settings

logger = logging.getLogger(__name__)


def configure_tracing() -> None:
    if settings.langfuse_enabled:
        logger.info("Langfuse tracing enabled for host=%s", settings.langfuse_host)
    else:
        logger.info("Langfuse tracing disabled; using no-op tracing.")
