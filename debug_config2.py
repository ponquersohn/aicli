#!/usr/bin/env python3

from pathlib import Path
from aicli.utils.config import Config

# Test the config loading with None values
try:
    config = Config.load(None, debug=False, verbose=False)  
    print(f"Config loaded successfully: {config}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()