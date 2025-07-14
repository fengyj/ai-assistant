#!/usr/bin/env python3
"""
Development server runner.
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from assistant.main import app
from assistant.core.config import config

if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting server on {config.host}:{config.port}")
    print(f"Debug mode: {config.debug}")
    
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=config.debug
    )
