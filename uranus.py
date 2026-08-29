import sys
import os
import subprocess

# تنظیم encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
else:
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# لیست پکیج‌های مورد نیاز
REQUIRED_PACKAGES = {
    "PyQt5": "PyQt5",
    "IPython": "IPython",
    "nbformat": "nbformat",
    "markdown2": "markdown2",
    "html2text": "html2text",
    "Pillow": "PIL",
    "ruff": "ruff"
}

def check_and_install(packages):
    missing = []
    for pkg_name, module_name in packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(pkg_name)

    if missing:
        print("🔧 Missing required packages:")
        for pkg in missing:
            print(f"  - {pkg}")
        print("Attempting automatic installation...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
            print("✅ Installation successful.")
        except Exception as e:
            print(f"❌ Automatic installation failed: {e}")
            print("Please install the missing packages manually:")
            print(f"pip install {' '.join(missing)}")
            sys.exit(1)

def main():
    print("📦 Checking dependencies...")
    check_and_install(REQUIRED_PACKAGES)
    
    print("🚀 Launching Uranus IDE...")
    
    # اضافه کردن مسیر src به sys.path
    project_root = os.path.dirname(os.path.abspath(__file__))
    src_path = os.path.join(project_root, "src")
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        # import مستقیم از src
        from core import main as uranus_main
        uranus_main()
    except ImportError as e:
        print(f"❌ Failed to import core: {e}")
        print("Make sure the project structure is correct:")
        print("  src/")
        print("  ├── __init__.py")
        print("  ├── core.py")
        print("  └── ...")
        sys.exit(1)

if __name__ == "__main__":
    main()