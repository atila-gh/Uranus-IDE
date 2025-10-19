# run_uranus.py — Manual launcher for Uranus IDE

import sys
import os



# Add src/ to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)
# Launch Uranus



sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from Uranus.core import main

main()