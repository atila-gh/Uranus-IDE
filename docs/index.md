# Uranus IDE — Technical Overview

Uranus is a modular, extensible Python IDE inspired by Jupyter, built with PyQt5. It supports interactive coding, markdown documentation, and structured output visualization — all within a clean, event-safe architecture.

## 🧱 Architecture Summary

- `core.py`: Entry point of the application. Initializes MainWindow and global settings.
- `MainWindow.py`: Hosts the MDI interface, file explorer, and menu system.
- `WorkWindow.py`: Manages individual notebook tabs and cell containers.
- `Cell.py`: Represents a code or markdown cell with execution/output logic.
- `CodeEditor.py`: Handles Python editing with syntax highlighting and smart indentation.
- `DocumentEditor.py`: Rich text editor for markdown cells.
- `OutputEditor.py`: Displays execution results (text, image, table).
- `SettingWindow.py`: Manages appearance and font settings.
- `ProjectInfoDialog.py`: Creates structured project folders with metadata and license.
- `utils.py`: Shared helpers and file operations.

## 📦 Folder Structure
uranus-ide/ 
        ├── src/Uranus/ 
        │   ├── core.py │  
            ├── MainWindow.py │   
            ├── WorkWindow.py │   
            ├── Cell.py │   
            ├── CodeEditor.py │   
            ├── OutputEditor.py │   
            ├── SettingWindow.py │   
            ├── ProjectInfoDialog.py │  
        └── ... ├── docs/ │   
                    └── index.md
        ├── tests/                # Reserved for future test scripts



## 🧠 Design Principles

- Modular class-based architecture
- Event-safe UI logic
- Explicit docstrings for all major classes
- Persian-English bilingual support
- Custom licensing and attribution enforcement

## 📚 Licensing

This project is governed by a custom license authored by Atila Ghashghaie.  
Commercial use, redistribution, or rebranding is strictly prohibited without written permission.  
See [LICENSE](../LICENSE) for full terms.

## ✉️ Contact

Developed by Atila Ghashghaie  
📧 atila.gh@gmail.com  
📞 +98 912 319 4008  
🌐 www.Puyeshmashin.ir