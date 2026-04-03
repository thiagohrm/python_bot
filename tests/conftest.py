"""
Pytest configuration file for test discovery and path setup.
Adds the parent directory to sys.path so tests can import the main module.
Mocks pyzbar to avoid system library dependency during testing.
"""
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Add the parent directory (project root) to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Mock pyzbar to avoid system library dependency during testing
sys.modules['pyzbar'] = MagicMock()
sys.modules['pyzbar.pyzbar'] = MagicMock()

