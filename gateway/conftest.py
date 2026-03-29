"""Pytest configuration for gateway tests."""

import sys
import os

# Add repository root to sys.path so 'from gateway.src.xxx' imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Add gateway directory so 'from src.xxx' imports work (used by cli.py, main.py)
sys.path.insert(0, os.path.dirname(__file__))
