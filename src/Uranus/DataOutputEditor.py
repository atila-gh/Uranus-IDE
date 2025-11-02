

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView,QHeaderView
from PyQt5.QtCore import Qt, QAbstractTableModel
from PyQt5.QtGui import QFont

class DataFrameModel(QAbstractTableModel):
    """
        A Qt-compatible table model for displaying pandas DataFrames in QTableView.

        Features:
        - Maps DataFrame rows and columns to Qt's model-view architecture.
        - Supports dynamic updates via set_dataframe().
        - Displays string representations of cell values.

        Parameters:
        - df (pd.DataFrame): Optional initial DataFrame to display.

        Methods:
        - rowCount(): Returns number of rows in the DataFrame.
        - columnCount(): Returns number of columns.
        - data(): Returns string value for each cell.
        - headerData(): Returns column or index labels for headers.

        Usage:
        Used internally by DataFrameWidget to render tabular data in the Uranus IDE.
        """

    def __init__(self, df=None, parent=None):
        super().__init__(parent)
        try :
            import pandas as pd
        except ImportError :
            return
        else :
            self._df = df if df is not None else pd.DataFrame()

    def rowCount(self, parent=None):
        return len(self._df)

    def columnCount(self, parent=None):
        return len(self._df.columns)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            value = self._df.iloc[index.row(), index.column()]
            return str(value)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role != Qt.DisplayRole:
            return None
        if orientation == Qt.Horizontal:
            return str(self._df.columns[section])
        else:
            return str(self._df.index[section])

class DataFrameWidget(QWidget):
    """
        A styled widget for displaying pandas DataFrames using QTableView.

        Features:
        - Automatically wraps a DataFrameModel and connects it to a sortable QTableView.
        - Supports alternating row colors and responsive layout.
        - Provides set_dataframe() method to update or clear the displayed data.

        Components:
        - QVBoxLayout: Contains the table view.
        - QTableView: Displays the DataFrame with headers and sorting enabled.
        - DataFrameModel: Custom model for mapping pandas data to Qt view.

        Usage:
        Used as the output viewer for table-type results in code cells.
        Can be embedded in scrollable containers and toggled via output buttons.
        """

    def __init__(self, parent=None):
        super().__init__(parent)

        try :
            import pandas as pd
        except ImportError:
            return

        self.setStyleSheet("background:white;")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.table = QTableView()
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)
       
        header_font = QFont("Segoe UI", 10, QFont.Bold)
        self.table.horizontalHeader().setFont(header_font)
        
        # self.table.horizontalHeader().setMinimumHeight(40)
        # self.table.horizontalHeader().setFixedHeight(40) 
        
        self.table.horizontalHeader().setStyleSheet("""
                                                        QHeaderView::section {
                                                            padding: 4px;
                                                            font-weight: bold;
                                                            background-color: #f0f0f0;
                                                            border: 1px solid #ccc;
                                                        }
                                                    """)

        
       

        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.model = DataFrameModel()
        self.table.setModel(self.model)

    def set_dataframe(self, df = None):
        """تنظیم یا پاک کردن DataFrame"""
        try :
            import pandas as pd
        except ImportError:
            return None
        else :
            self.model = DataFrameModel(df)
            self.table.setModel(self.model)


