import os ,sys
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false"
os.environ["QT_PLUGIN_PATH"] = ""   


from importlib.metadata import version, PackageNotFoundError
import importlib.util
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import QApplication, QStyleFactory


current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)



from MainWindow import MainWindow




def install_fonts():
    # font folder is a sibling of this file
    font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "font")

    font_files = [
        "JetBrainsMono-Light.ttf",
        "Technology.ttf",
        "SpaceMono-Regular.ttf",
    ]

    existing_fonts = set(QFontDatabase().families())

    for font_file in font_files:
        font_path = os.path.join(font_dir, font_file)
        try:
            with open(font_path, "rb") as f:
                font_data = f.read()
            font_id = QFontDatabase.addApplicationFontFromData(font_data)
            if font_id == -1:
                print(f"⚠️ Failed to load font: {font_file}")
            else:
                loaded = QFontDatabase.applicationFontFamilies(font_id)
                print(f"✅ Font installed: {loaded[0] if loaded else font_file}")
        except FileNotFoundError:
            print(f"❌ Font file not found: {font_path}")
        except Exception as e:
            print(f"❌ Error loading '{font_file}': {e}")

    newly_added = set(QFontDatabase().families()) - existing_fonts
    if newly_added:
        print("\n📋 Fonts added by Uranus:")
        for f in sorted(newly_added):
            print(f"  • {f}")
    else:
        print("\nℹ️ No new fonts were added.")

def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")
    install_fonts()
    print(f"🚀 Uranus IDE v{get_version()}")
    print("🎨 Available styles:", QStyleFactory.keys())

    # For Dark Mode
    #import qdarktheme
    #qdarktheme.setup_theme("dark")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

def get_version():
    try:
        return version("Uranus-IDE")
    except PackageNotFoundError:
        return "0.0.0-dev"


if __name__ == "__main__":
    main()


