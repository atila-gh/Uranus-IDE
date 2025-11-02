# Uranus IDE — Technical Overview

<h2 align="center">Uranus IDE Screenshots</h2>

<table align="center">
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-1.png"
           alt="Uranus IDE main interface by Atila Ghashghaie - آتیلا قشقایی "
           title="Uranus IDE - Main Interface by Atila Ghashghaie - آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 1</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-2.png"
           alt="Uranus IDE code editor by Atila Ghashghaie - آتیلا قشقایی "
           title="Uranus IDE - Code Editor by Atila Ghashghaie - آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 2</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-3.png"
           alt="Uranus IDE settings panel by Atila Ghashghaie - آتیلا قشقایی "
           title="Uranus IDE - Settings Panel by Atila Ghashghaie - آتیلا قشقایی i"
           width="300"><br>
      <em>Screenshot 3</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-4.png"
           alt="Uranus IDE file explorer by Atila Ghashghaie - آتیلا قشقایی "
           title="Uranus IDE - File Explorer by Atila Ghashghaie - آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 4</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-5.png"
           alt="Uranus IDE project manager by Atila Ghashghaie - آتیلا قشقایی "
           title="Uranus IDE - Project Manager by Atila Ghashghaie - آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 5</em>
    </td>
    <td></td>
  </tr>
</table>

<p align="center">
  Screenshots from Uranus IDE — created and developed by <strong>Atila Ghashghaie - آتیلا قشقایی </strong>.
</p>


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