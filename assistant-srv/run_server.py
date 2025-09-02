#!/usr/bin/env python3
"""
Start the Personal AI Assistant Server.
"""

import logging
import os
import sys

import uvicorn

from assistant.core.env import Env

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from assistant.core import config  # noqa: E402
from assistant.utils.db_init import initialize_database  # noqa: E402

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point."""
    logger.info("Starting Personal AI Assistant Server...")

    # Initialize database
    initialize_database()

    # Start server
    uvicorn.run(
        "assistant.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_config=Env.get_log_config(),
    )


if __name__ == "__main__":
    main()
