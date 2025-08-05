#!/usr/bin/env python3
"""
Start the Personal AI Assistant Server.
"""

import sys
import os
import uvicorn
from dotenv import load_dotenv
env_suffix = os.getenv('ENV', '')
env_file = f".env{'.' + env_suffix if env_suffix else ''}"
load_dotenv(dotenv_path=env_file)
load_dotenv(dotenv_path=f"{env_file}.local")  # Load default .env if exists

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from assistant.core.config import config
from assistant.utils.db_init import initialize_database


def main():
    """Main entry point."""
    print("Starting Personal AI Assistant Server...")

    # Initialize database
    initialize_database()

    # Start server
    uvicorn.run(
        "assistant.main:app",
        host=config.host,
        port=config.port,
        reload=config.debug,
        log_level="info" if not config.debug else "debug",
    )


if __name__ == "__main__":
    main()
