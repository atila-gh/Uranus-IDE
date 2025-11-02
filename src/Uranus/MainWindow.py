import json , nbformat , os
from PyQt5 import sip
from PyQt5.QtWidgets import  QMainWindow, QWidget, QVBoxLayout, QToolBar, QToolButton, QDockWidget  , QMessageBox , QMdiArea, QAction , QFileDialog ,QMessageBox
from PyQt5.QtGui import QIcon 
from PyQt5.QtCore import Qt, QSize , QEvent


from Uranus.utils import FileTreeView , FileTreePanel
 # Make sure your FileTreeView is updated as below
from Uranus.WorkWindow import WorkWindow 
from Uranus.SettingWindow import SettingsWindow , load_setting
from Uranus.PythonTemplate import ProjectInfoDialog
from Uranus.AboutWindow import AboutWindow



# noinspection PyUnresolvedReferences
class MainWindow(QMainWindow):


    open_files = {}  # dict: file_path -> WorkWindow instance
    """
        The main application window for Uranus IDE.

        This class serves as the central controller for the IDE, managing file operations,
        dockable widgets, project structure, and multiple open notebooks via QMdiArea.

        Key Responsibilities:
        - Hosts multiple WorkWindow instances as subwindows (MDI architecture).
        - Manages file tree navigation, selection, and double-click opening.
        - Provides toolbars for file/folder creation, deletion, and project setup.
        - Loads and saves .ipynb files using nbformat.
        - Stores open file references to prevent duplicate subwindows.
        - Integrates settings, about dialog, and project metadata via external modules.

        Components:
        - QMdiArea: Central workspace for notebook tabs.
        - QDockWidget: File explorer with toolbar and tree view.
        - QToolBar: Left and top toolbars for quick actions.
        - FileTreeView: Custom tree view for filesystem navigation.
        - WorkWindow: Editor container for code and markdown cells.

        Class Variables:       
        - open_files (dict): Maps file paths to active WorkWindow subwindows.

        Usage:
        This class is instantiated at application startup and remains active throughout
        the user session. It coordinates user interactions, file management, and UI layout.
        """

    def __init__(self):
        super().__init__()
        

        self.debug = False
        self.setting = load_setting()

        self.setWindowTitle("Uranus")
        self.setGeometry(100, 100, 1000, 1000)
        self.showMaximized()
        

        icon_path = os.path.join(os.path.dirname(__file__), "image", "Uranus.png")   
        self.setWindowIcon(QIcon(icon_path))

        # MDI Area: central widget to hold multiple WorkWindows
        self.mdi_area = QMdiArea()
        self.setCentralWidget(self.mdi_area)
        self.mdi_area.subWindowActivated.connect(self.sync_working_directory)
        

        # Set up the status bar
        self.mainwindow_statusbar = self.statusBar()
        self.statusBar().showMessage("Ready")
        self.statusBar().setStyleSheet("QStatusBar { border-top: 1px solid gray; }")
        

        # Initialize UI components
        self.init_ui()

    def init_ui(self):

        # Tree View Model 
        self.tree = FileTreePanel()
        # Connect the clicked signal to update the selected path
        self.tree.installEventFilter(self)
        self.tree.tree.doubleClicked.connect(self.on_tree_item_double_clicked) # Event On DoubleClick
        self.tree.tree.pathChanged.connect(self.on_path_changed)

        # ----------------------------- MENU BAR -----------------------------
        
        menubar = self.menuBar()

        # --- File Menu ---
        file_menu = menubar.addMenu("File")

        new_file_action = QAction("New File", self)
        new_file_action.setShortcut("Ctrl+N")
        new_file_action.triggered.connect(self.tree.tree.create_file)  
        file_menu.addAction(new_file_action)

        new_folder_action = QAction("New Folder", self)
        new_folder_action.setShortcut("Ctrl+Shift+N")
        new_folder_action.triggered.connect(self.tree.tree.create_folder)
        file_menu.addAction(new_folder_action)

        file_menu.addSeparator()
        
        open_file = QAction("Open File", self)      
        open_file.setShortcut("Ctrl+O") 
        open_file.triggered.connect(self.open_ipynb_file)
        file_menu.addAction(open_file)
        
        file_menu.addSeparator()        
        
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.trigger_save_on_active_workwindow)
        file_menu.addAction(save_action)

 
        save_as = QAction("Save As", self)   
        save_as.setShortcut("Ctrl+Shift+S")     
        save_as.triggered.connect(self.save_as_file)
        file_menu.addAction(save_as)
        
        file_menu.addSeparator() 

      
        settings_action = QAction("Setting", self)
        settings_action.triggered.connect(self.open_settings_window)
        file_menu.addAction(settings_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # --- Edit Menu ---
        edit_menu = menubar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut("Ctrl+Z")
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut("Ctrl+Y")
        edit_menu.addAction(redo_action)
       
        file_menu.addSeparator()

        find_action = QAction("Find", self)
        find_action.setShortcut("Ctrl+F")
        find_action.triggered.connect(self.trigger_find_on_active_workwindow)
        edit_menu.addAction(find_action)


         # --- Window Menu ---
        window_menu = menubar.addMenu("Window")

        cascade_action = QAction("Cascade", self)
        cascade_action.triggered.connect(self.mdi_area.cascadeSubWindows)
        window_menu.addAction(cascade_action)

        tile_action = QAction("Tile", self)
        tile_action.triggered.connect(self.mdi_area.tileSubWindows)
        window_menu.addAction(tile_action)

        window_menu.addSeparator()

        close_all_action = QAction("Close All", self)
        close_all_action.triggered.connect(self.mdi_area.closeAllSubWindows)
        window_menu.addAction(close_all_action)

        # --- Help Menu ---
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self.about)
        help_menu.addAction(about_action)



        # ----------------------------- LEFT TOOLBAR -----------------------------
        # Toggle Dock Button Icon
        icon_path = os.path.join(os.path.dirname(__file__), "image", "File_Tree.png")
        self.toggle_btn = QToolButton()
        self.toggle_btn.setIcon(QIcon(icon_path))
        self.toggle_btn.setToolTip("Show File Explorer")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self.toggle_dock_tree)
        self.toggle_btn.setIconSize(QSize(32, 32))


        # Create Project Button
        icon_path = os.path.join(os.path.dirname(__file__), "image", "create_project.png")  # آیکون دلخواه
        self.create_project_btn = QToolButton()
        self.create_project_btn.setIcon(QIcon(icon_path))
        self.create_project_btn.setToolTip("Create Project from Selected Folder")
        self.create_project_btn.setIconSize(QSize(32, 32))
        self.create_project_btn.clicked.connect(self.create_project_from_selected_folder)



        # Left vertical toolbar
        toolbar_main_left = QToolBar()
        toolbar_main_left.setOrientation(Qt.Vertical)
        toolbar_main_left.setContextMenuPolicy(Qt.PreventContextMenu)
        self.addToolBar(Qt.LeftToolBarArea, toolbar_main_left)
        toolbar_main_left.addWidget(self.toggle_btn)
        toolbar_main_left.addWidget(self.create_project_btn)




        # ----------------------------- TOP DOCK TOOLBAR -----------------------------


        # Open Project Folder
        icon_path = os.path.join(os.path.dirname(__file__), "image", "prj_folder.png")  # آیکون دلخواه
        self.select_folder_btn = QToolButton()
        self.select_folder_btn.setIcon(QIcon(icon_path))
        self.select_folder_btn.setToolTip("Select Project Folder")
        
        self.select_folder_btn.clicked.connect(self.select_project_folder)
        self.select_folder_btn.setIconSize(QSize(48, 48))

        # Add Folder Button
        icon_path = os.path.join(os.path.dirname(__file__), "image", "add_folder.png")
        self.add_folder_btn = QToolButton()
        self.add_folder_btn.setIcon(QIcon(icon_path))
        self.add_folder_btn.setToolTip("Add Folder")
        self.add_folder_btn.clicked.connect(self.tree.tree.create_folder)
        self.add_folder_btn.setIconSize(QSize(32, 32))

        # Add File Button
        icon_path = os.path.join(os.path.dirname(__file__), "image", "add_file.png")
        self.add_file_btn = QToolButton()
        self.add_file_btn.setIcon(QIcon(icon_path))
        self.add_file_btn.setToolTip("Add File")
        self.add_file_btn.clicked.connect(self.tree.tree.create_file)
        self.add_file_btn.setIconSize(QSize(32, 32))


        # Top horizontal toolbar
        self.dock_top_toolbar = QToolBar()
        self.dock_top_toolbar.addWidget(self.select_folder_btn)
        self.dock_top_toolbar.addWidget(self.add_file_btn)
        self.dock_top_toolbar.addWidget(self.add_folder_btn)


        # ----------------------------- FILE TREE VIEW -----------------------------

        # Layout for dock content
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.dock_top_toolbar)
        layout.addWidget(self.tree)

        # Create a QWidget as dock content
        dock_content = QWidget()
        dock_content.setLayout(layout)

        # ----------------------------- DOCK WIDGET -----------------------------
        self.dock = QDockWidget("File Explorer", self)
        self.dock.setWidget(dock_content)
        self.dock.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetClosable)
        self.dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.dock)
        # حذف هدر پنجره
        self.dock.setTitleBarWidget(QWidget())

    def toggle_dock_tree(self):
        """Show or hide the file explorer dock based on toggle button state"""
        visible = self.toggle_btn.isChecked()
        self.dock.setVisible(visible)
      
    def on_tree_item_double_clicked(self, index):
        path = self.tree.tree.fs_model.filePath(index)


        if os.path.isfile(path):
            _, ext = os.path.splitext(path)
            ext = ext.lower()

            if ext == ".ipynb":
                existing_subwindow = MainWindow.open_files.get(path)

                if existing_subwindow and not sip.isdeleted(existing_subwindow):

                    self.mdi_area.setActiveSubWindow(existing_subwindow)
                else:

                    if os.path.getsize(path) > 0:
                        self.ipynb_format_load_file(path)
                        
                    else:
                        work_widget = WorkWindow(file_path=path , status = self.mainwindow_statusbar )
                        sub_window = self.mdi_area.addSubWindow(work_widget)


                        sub_window.destroyed.connect(lambda: MainWindow.open_files.pop(path, None))

                        sub_window.show()
                        MainWindow.open_files[path] = sub_window


    def eventFilter(self, source, event):
        if source == self.tree and event.type() == QEvent.KeyPress:
            if event.key() in (Qt.Key_Return, Qt.Key_Enter):
                index = self.tree.tree.currentIndex()
                if index.isValid():
                    path = self.tree.tree.fs_model.filePath(index)
                    if os.path.isfile(path):
                        self.on_tree_item_double_clicked(index)
                        return True
        return super().eventFilter(source, event)


    def ipynb_format_load_file (self , path):
        if self.debug : print('[MainWindow]->[ipynb_format_load_file]')
        try:
            with open(path, "r", encoding="utf-8") as f:
                nb = nbformat.read(f, as_version=4)
        
        except UnicodeDecodeError as e:
            QMessageBox.warning(self, "Encoding Error", f"Cannot decode file:\n{e}")
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "JSON Error", f"Invalid JSON format:\n{e}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unexpected error:\n{e}")

        # Make Instance Object
        work_widget = WorkWindow(file_path=path , content = nb , status = self.mainwindow_statusbar)
        sub_window = self.mdi_area.addSubWindow(work_widget)
        sub_window.show()
        MainWindow.open_files[path] = sub_window

    def open_settings_window(self):
        self.settings_window = SettingsWindow()
        self.settings_window.show()

    def select_project_folder(self, path=None):
        folder_path = path or QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if not folder_path:
            return


        # تنظیم مسیر در FileTreeView به‌صورت دستی
        self.tree.tree.path = folder_path
        self.tree.tree.project_root = folder_path
        self.tree.tree.fs_model.setRootPath(folder_path)
        self.tree.tree.setRootIndex(self.tree.tree.fs_model.index(folder_path))
        self.tree.tree.pathChanged.emit(folder_path)

        # refresh the current path on top of the tree view label
        self.dock.setWindowTitle(f"Project: {os.path.basename(folder_path)}")

        # save the last path in setting file
        self.setting['last_path'] = folder_path
        self.save_settings(self.setting)
        os.chdir(folder_path)



    def create_project_from_selected_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if not folder_path:
            return

        project_name = os.path.basename(folder_path.strip())
        if not project_name:
            QMessageBox.warning(self, "Invalid Folder", "Selected folder name is empty.")
            return

        dialog = ProjectInfoDialog(project_name, folder_path, self)
        dialog.exec()

        self.select_project_folder(path = folder_path)

    @staticmethod
    def save_settings(setting):
       current_file = os.path.abspath(__file__)  # src/Uranus/SettingWindow.py
       src_dir = os.path.dirname(os.path.dirname(current_file))  # ← src/
       path =  os.path.join(src_dir, "setting.json")

       try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(setting, f, indent=4, ensure_ascii=False)
       except FileNotFoundError :
           return

    def about(self):
        about_window = AboutWindow()
        about_window.show()
        self.about_window = about_window

    @staticmethod
    def on_path_changed(path):
        if os.path.isfile(path):
            path = os.path.dirname(path)

    def save_as_file(self):
        """
        Prompts the user to choose a new file path and delegates saving to the active WorkWindow.
        """
        

        active_subwindow = self.mdi_area.activeSubWindow()
        if not active_subwindow:
            QMessageBox.warning(self, "No Active File", "No notebook is currently open.")
            return

        work_widget = active_subwindow.widget()
        if not isinstance(work_widget, WorkWindow):
            QMessageBox.warning(self, "Invalid Window", "Active window is not a notebook.")
            return

        new_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save As",
            work_widget.file_path or "",
            "Jupyter Notebook (*.ipynb)"
        )

        if not new_path:
            return

        try:
            work_widget.file_path = new_path
            work_widget.ipynb_format_save_file()
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Could not save file:\n{e}")
        else:
            self.statusBar().showMessage("Saved As: " + new_path)
            
            
            
    def open_ipynb_file(self):
        """
        Opens a file dialog to select a .ipynb file and loads it into a new WorkWindow.
        Only accepts valid Jupyter Notebook files.
        """
       

        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Notebook",
            "",
            "Jupyter Notebook (*.ipynb)"
        )

        if not path:
            return  # کاربر لغو کرده

        if not os.path.isfile(path) or not path.lower().endswith(".ipynb"):
            QMessageBox.warning(self, "Invalid File", "Selected file is not a valid .ipynb notebook.")
            return

        # بررسی اینکه آیا قبلاً باز شده
        existing_subwindow = MainWindow.open_files.get(path)
        if existing_subwindow and not sip.isdeleted(existing_subwindow):
            self.mdi_area.setActiveSubWindow(existing_subwindow)
            return

        # بارگذاری فایل
        self.ipynb_format_load_file(path)
        
        
    def trigger_save_on_active_workwindow(self):
        active_subwindow = self.mdi_area.activeSubWindow()
        
        if not active_subwindow:
            return
        work_widget = active_subwindow.widget()
        if hasattr(work_widget, "ipynb_format_save_file"):
            work_widget.ipynb_format_save_file()

    def trigger_find_on_active_workwindow(self):
        active_subwindow = self.mdi_area.activeSubWindow()
        if not active_subwindow:
            return
        work_widget = active_subwindow.widget()
        if hasattr(work_widget, "find_replace"):
            work_widget.find_replace()
            
            
    def sync_working_directory(self, subwindow):
        """
        Syncs the system working directory with the active WorkWindow's file path.
        Called whenever the active subwindow changes.
        """
        if not subwindow:
            return

        widget = subwindow.widget()
        if hasattr(widget, "file_path") and widget.file_path:
            folder = os.path.dirname(widget.file_path)
            if os.path.exists(folder):
                try:
                    os.chdir(folder)                    
                    self.statusBar().showMessage('[Current Folder] '+folder)
                except Exception as e:
                    print(f"⚠️ Failed to set working directory: {e}")