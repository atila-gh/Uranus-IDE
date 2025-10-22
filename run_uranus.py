import sys
import os
import subprocess

# List of required packages
REQUIRED_PACKAGES = [
    "PyQt5",
    "IPython",
    "nbformat",
    "markdown2",
    "html2text"
    

    # Add more if needed
]

def check_and_install(packages):
    missing = []
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print("🔧 Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("Attempting automatic installation...")

        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("✅ Installation successful.")
        except Exception :
            print("❌ Automatic installation failed.")
            print("Please install the missing packages manually:")
            print(f"pip install {' '.join(missing)}")
            sys.exit(1)

# Check dependencies before launching
print("📦 Checking dependencies...")
check_and_install(REQUIRED_PACKAGES)

# Add src/ to sys.path
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

# Launch Uranus
print("🚀 Launching Uranus IDE...")
from Uranus.core import main
main()