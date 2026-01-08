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

    is_tty = sys.stdout.isatty()

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,  # Better for large traces
            structlog.processors.TimeStamper(fmt="iso", utc=True),  # Standard ISO
            structlog.dev.ConsoleRenderer(colors=True)
            if is_tty
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        # Factory choice: Print is more secure for interoperability with 'tee'
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


log = structlog.get_logger()
