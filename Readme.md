# Uranus IDE

Uranus is a lightweight, extensible Python IDE inspired by Jupyter. It supports interactive coding, markdown documentation, and modular plugin architecture — all built with PyQt5.

> 🔥 **Uranus IDE is the first modular Python IDE with full RTL support across all editing modes.**


<h2 align="left">Uranus IDE Screenshots</h2>

<table align="left">
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


## Features

- 🧠 Code and Markdown cells with live execution
- 📊 Output viewers for text, tables, and images
- 🧰 Customizable toolbar and editor settings
- 🧾 Project scaffolding with license and metadata
- 🧱 File explorer with context menu and keyboard shortcuts


### ✨ Key Features

- ✅ Cell-based editing with IPython kernel
- ✅ Modular architecture with PyQt5
- ✅ **Full RTL (Right-to-Left) support** for Persian, Arabic, and other RTL languages
- ✅ Custom file explorer with inline editing
- ✅ Project creation and metadata management


## 🧩 Advanced Window & Memory Features

Uranus IDE goes beyond traditional editors by introducing two powerful features that elevate both usability and introspection:

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

These features are designed and implemented by [Atila Ghashghaie](https://github.com/atila-gh) — bringing modular architecture and deep introspection to the heart of Python development.

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


