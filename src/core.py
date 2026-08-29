import os
import sys
import importlib.util
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QStyleFactory

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from MainWindow import MainWindow




def install_fonts():
    """
    Installs custom fonts required by Uranus IDE.
    Compatible with both source-based execution and pip-installed package mode.
    """

    try:
        from Uranus import font
    except ImportError:
        print("❌ Font package not found. Ensure 'src/Uranus/font/' contains __init__.py.")
        return

    font_files = [
        "JetBrainsMono-Light.ttf",          
        "Technology.ttf",
        "SpaceMono-Regular.ttf",

    ]

    existing_fonts = set(QFontDatabase().families())

    for font_file in font_files:
        font_path = os.path.join(os.path.dirname(font.__file__), font_file)
        try:
            with open(font_path, "rb") as f:
                font_data = f.read()
                font_id = QFontDatabase.addApplicationFontFromData(font_data)

            if font_id == -1:
                print(f"⚠️ Failed to load font: {font_file}")
            else:
                loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)
                print(f"✅ Font installed: {loaded_fonts[0] if loaded_fonts else font_file}")
        except Exception as e:
            print(f"❌ Error loading font '{font_file}': {e}")

    updated_fonts = set(QFontDatabase().families())
    newly_added = updated_fonts - existing_fonts

    if newly_added:
        print("\n📋 Fonts added by Uranus:")
        for font in sorted(newly_added):
            print(f"  • {font}")
    else:
        print("\nℹ️ No new fonts were added (they may already be installed).")

def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    install_fonts()
    print("🎨 Available styles:", QStyleFactory.keys())

    # For Dark Mode
    #import qdarktheme
    #qdarktheme.setup_theme("dark")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


