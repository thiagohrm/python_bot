"""
Pytest configuration file for test discovery and path setup.
Adds the parent directory to sys.path so tests can import the main module.
"""
import sys
from pathlib import Path

# Add the parent directory (project root) to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
