#!/usr/bin/env python3
"""
Talks: Multi-Agent Philosophical Discussion System
"""

import sys
from src.cli.client import main
from src.config import TalksConfig

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

# Initialize configuration
config = TalksConfig()

if __name__ == "__main__":
    sys.exit(main())