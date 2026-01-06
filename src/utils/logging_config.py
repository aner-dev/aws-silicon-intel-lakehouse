# src/logging_config.py
import logging
import sys
import structlog


def setup_logging():
    # 1. Config standard logging as it redirect to structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,  # Better for large traces
            structlog.processors.TimeStamper(fmt="iso", utc=True),  # Standard ISO
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.BytesLoggerFactory()
        if sys.stdout.isatty() is False
        else structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,  # RELEVANT for performance
    )


log = structlog.get_logger()
