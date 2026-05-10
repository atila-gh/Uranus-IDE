# Uranus IDE
**Author:** Attila Ghashghaei | آتیلا قشقایی


### About the Author :  
Attila Ghashghaei (آتیلا قشقایی)  
**Uranus IDE is a Python IDE developed in Iran,
designed specifically for RTL languages
including Persian, Arabic, Hebrew, Urdu, and others.**

**🔗 Project Repository: https://github.com/atila-gh/Uranus-IDE**   
**🔗 Personal Site : https://puyeshmashin.ir**   
**🔗LinkedIn       :  linkedin.com/in/atila-gh**  
**🔗PyPi           : pypi.org/user/atila.gh**  

 ## 🇮🇷 National IDE Position

Uranus IDE is designed and developed in Iran as a **National Python IDE** with full support for Persian and RTL languages.  
This project aims to provide a local, independent,
and open-source development environment for Iranian developers,
educators, and industrial users.

### About Uranus-IDE  

Uranus is a lightweight, extensible Python IDE inspired by Jupyter. It supports interactive coding, markdown documentation, and modular plugin architecture — all built with PyQt5.

> 🔥 **Uranus IDE is the first modular Python IDE with full RTL support across all editing modes.**


<h2 align="left">Uranus IDE Screenshots</h2>

<table align="left">
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-1.png"
           alt="Uranus IDE main interface by Attila Ghashghaei | آتیلا قشقایی "
           title="Uranus IDE - Main Interface by Attila Ghashghaei |  آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 1</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-2.png"
           alt="Uranus IDE code editor by Attila Ghashghaei |  آتیلا قشقایی "
           title="Uranus IDE - Code Editor by Attila Ghashghaei |  آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 2</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-3.png"
           alt="Uranus IDE settings panel by Attila Ghashghaei |  آتیلا قشقایی "
           title="Uranus IDE - Settings Panel by Attila Ghashghaei |  آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 3</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-4.png"
           alt="Uranus IDE file explorer by Attila Ghashghaei |   آتیلا قشقایی "
           title="Uranus IDE - File Explorer by Attila Ghashghaei |   آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 4</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-5.png"
           alt="Uranus IDE project manager by Attila Ghashghaei |  آتیلا قشقایی "
           title="Uranus IDE - Project Manager by Attila Ghashghaei |  آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 5</em>
    </td>
    <td align="center">
      <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-6.png"
           alt="Uranus IDE project manager by Attila Ghashghaei |  آتیلا قشقایی "
           title="Uranus IDE - Project Manager by Attila Ghashghaei |  آتیلا قشقایی "
           width="300"><br>
      <em>Screenshot 6</em>
    </td>

    
  </tr>
</table>

<p align="center">
  Screenshots from Uranus IDE — created and developed by <strong>Attila Ghashghaei |  آتیلا قشقایی </strong>.
</p>


## Overview

- 🧠 Code and Markdown cells with live execution
- 📊 Output viewers for text, tables, and images
- 🧰 Customizable toolbar and editor settings
- 🧾 Project scaffolding with license and metadata
- 🧱 File explorer with context menu and keyboard shortcuts


### ✨ Detailed

- ✅ Cell-based editing with IPython kernel
- ✅ Modular architecture with PyQt5
- ✅ **Full RTL (Right-to-Left) support** for Persian, Arabic, and other RTL languages
- ✅ Custom file explorer with inline editing
- ✅ Project creation and metadata management





## ✨ Intelligent AutoComplete System

Uranus IDE features a **smart, context-aware auto-completion system** that significantly accelerates Python coding. Built directly into the code editor, this system provides intelligent suggestions for:

### 🔍 Key Features

| Feature | Description |
|---------|-------------|
| **🧠 Context-Aware Suggestions** | Detects module contexts (e.g., `np.` suggests NumPy functions) and global Python keywords, builtins, and user-defined symbols |
| **⚡ On-Demand Activation** | Trigger suggestions instantly with `Ctrl+Space` — just like IDLE and professional IDEs |
| **🎨 Color-Coded Items** | Builtins appear in white, Python keywords in orange-red, module-specific items in specialized colors for quick visual identification |
| **📚 Documentation Popup** | Each suggestion includes a **signature**, **docstring**, and **source module** displayed in a side popup for immediate reference |
| **🎯 Smart Ranking** | Suggestions are intelligently ranked: builtins first → keywords → module items, with shorter and more relevant names prioritized |
| **⌨️ Full Keyboard Navigation** | Navigate the list using `↑`/`↓`, `PageUp`/`PageDown`, `Home`/`End`, and accept with `Enter`, `Tab`, or mouse click |
| **🔘 Toggle On/Off** | A dedicated toolbar button allows you to enable or disable the auto-completion system at any time |
| **📦 Extensible Database** | Auto-completion data is stored in `autocomplete_db.json`, making it easy to add support for additional modules, libraries, or custom APIs |

### 🖼️ How It Works

1. **Type your code** — as you type, nothing happens until you need assistance
2. **Press `Ctrl+Space`** — the suggestion list appears at the cursor position
3. **Navigate** — use arrow keys to browse through suggestions
4. **View documentation** — each selected item shows its signature and docstring
5. **Accept** — press `Enter`, `Tab`, or click to insert the complete word

<p align="center">
  <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/Uranus-IDE-7.png"  width="400">
</p>



## 🐍 Python Error & Lint Testing

Uranus IDE integrates a **built‑in error and lint analyzer** powered by [Ruff](https://github.com/astral-sh/ruff).  
This feature allows developers to run static analysis directly inside the IDE and instantly detect:

- ❌ **Syntax and style errors** (indentation, spacing, line length, etc.)  
- ⚠️ **Warnings** for risky or non‑optimal code patterns  
- 🧩 **Unused imports, undefined names, and logical issues**  
- 📏 **Customizable rule categories** with checkboxes for enabling/disabling specific families (e.g. `E`, `W`, `F`, `B`, `UP`)  
- 🎨 **Color‑coded output highlighting** for errors, warnings, and success messages  

The analyzer window provides a **dark‑themed interface** with live feedback and a status bar that displays rule descriptions when hovering over checkboxes. Developers can tailor the analysis to their workflow by ignoring selected categories and re‑running checks with a single click.

> With this addition, Uranus IDE becomes not only an interactive coding environment but also a **powerful linting and error‑testing tool** for Python projects.

### 🔀 Detachable WorkWindows — Seamless Floating Mode

Switch any notebook window between embedded (MDI) and floating mode with a single click — without losing content, focus, or execution state. This feature enables:

- Multi-monitor workflows with independent execution panels
- Persistent cell layout and toolbar state across transitions
- Instant toggling via the "Detach" checkbox in the top toolbar

> Built with robust parent migration logic, Uranus ensures that every cell, output, and toolbar remains intact during window transitions.

---

### 🧠 Attribute Table — Inspect Your Runtime Like a Pro

Uranus includes a dynamic attribute inspector that visualizes all user-defined variables and objects in a structured table:

| Name         | Type     | Size (bytes) | Value Preview |
|--------------|----------|--------------|----------------|
| `df`         | DataFrame| 2048         | `<table>`      |
| `img`        | Image    | 5120         | `<image>`      |
| `model`      | Class    | 1024         | `<object>`     |

Features:
- Recursively inspects attributes of user-defined classes and instances
- Filters internal and unsupported types for clarity
- Displays live memory footprint and object type
- Fully integrated with IPython kernel and object store

> Whether you're debugging a complex pipeline or teaching data structures, this table gives you full visibility into your runtime environment.

---

These features are designed and implemented by [Attila Ghashghaei | آتیلا قشقایی](https://github.com/atila-gh) — bringing modular architecture and deep introspection to the heart of Python development.

### Python Script Editor 
This module provides a dedicated Python editor and console inside Uranus IDE.  
It can display and edit `.py` files, run them in Python kernel.

### 📝 Comment Headings

Uranus IDE now supports special formatting for comments:

- `##` makes the comment font **2 points larger** than normal.  
- `###` makes the comment font **4 points larger** and **bold**.  

This allows you to create **visual headings inside your code** for better readability and teaching.

<p align="center">
  <img src="https://raw.githubusercontent.com/atila-gh/Uranus-IDE/main/docs/images/comment.png"  width="400">
</p>


### 📝 Independent Markdown Editor

Uranus IDE now includes a **dedicated Markdown editor** that operates independently from the code environment.  
This editor provides a professional space for writing and managing documentation, tutorials, and project notes.  
Key benefits include:

- Full support for standard Markdown syntax (headings, lists, tables, images, links)
- A distraction-free environment tailored for documentation
- Ideal for creating technical reports, teaching materials, or project guides

With this addition, Uranus IDE becomes not only a coding platform but also a complete solution for **professional documentation workflows**.

---

### ⏱ Code Cell Execution Timer

Each code cell in Uranus IDE is now equipped with an **execution time display**.  
This feature automatically measures:

- The total runtime of the current cell execution
- The **delta** (difference) compared to the previous execution of the same cell

This allows developers and educators to:

- Benchmark performance changes between runs
- Identify bottlenecks in code execution
- Gain immediate feedback on optimization efforts

By integrating execution timing directly into the cell interface, Uranus IDE makes performance analysis seamless and intuitive.

---

## Installation and Run Project After GitHub Cloning 

1- Go to Project Folder  -> Uranus-IDE\
```bash
pip install -r requirements.txt
python uranus.py
```
## Installation and Run With pip install from Pypi.org
1 - go to cmd or terminal
```bash
pip install Uranus-IDE
```
2 after finishing just type in termainal or cmd 
```bash
uranus
```
## Update Project to the Last Version in Pypi.org
1 - go to cmd or terminal
```bash
# Recomended Method
pip uninstall uranus-ide
pip install uranus-ide
```
OR 

```bash
pip install --upgrade uranus-ide

```


