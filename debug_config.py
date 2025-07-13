#!/usr/bin/env python3

from pathlib import Path
from aicli.utils.config import Config

# Test the config loading
try:
    yaml_file = Config._find_config_file()  
    print(f"yaml_file type: {type(yaml_file)}")
    print(f"yaml_file value: {yaml_file}")
    if yaml_file:
        print(f"yaml_file.exists type: {type(yaml_file.exists)}")
        print(f"yaml_file.exists(): {yaml_file.exists()}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()