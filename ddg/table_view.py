from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QApplication
from PyQt5 import QtGui, QtCore

class TableView(QDialog):
    def __init__(self, data, *args):
        QDialog.__init__(self, *args)
        self.verticalLayout = QVBoxLayout(self)
        self.table = QTableWidget(parent=self)
        self.nrows = len(data)
        self.ncols = len(data[0])
        # print(self.nrows, self.ncols)
        self.table.setRowCount(self.nrows)
        self.table.setColumnCount(self.ncols)
        self.verticalLayout.addWidget(self.table)
        self.setLayout(self.verticalLayout)
        self.data = data
        self.setData()
        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        h = self.table.verticalHeader().length()
        w = self.table.horizontalHeader().length()
        self.resize(int(w*1.3), int(h*1.3))
        self.setWindowTitle("BOM Preview")
        self.ctrl = False

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        key = event.key()
        if key == QtCore.Qt.Key_Control:
            self.ctrl = True
        elif key == QtCore.Qt.Key_C:
            if self.ctrl:
                self.copy_cells_to_clipboard()

    def keyReleaseEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Control:
            self.ctrl = False
        
    def copy_cells_to_clipboard(self):
        if len(self.table.selectionModel().selectedIndexes()) > 0:
            # sort select indexes into rows and columns
            previous = self.table.selectionModel().selectedIndexes()[0]
            previous_row = previous.column()
            columns = []
            rows = []
            clipboard = ""

            for index in self.table.selectionModel().selectedIndexes():
                index_row = index.row()
                if previous_row != index_row:
                    rows.append(columns)
                    columns = []
                columns.append(index.data())
                previous_row = index_row
            columns.append(rows)

            # add rows and columns to clipboard            
            nrows = len(rows)
            ncols = len(rows[0])
            for r in range(nrows):
                for c in range(ncols):
                    text = str(rows[r][c])
                    if not text: text = ""
                    clipboard += text
                    if c != (ncols-1):
                        clipboard += '\t'
                clipboard += '\r\n'

            # copy to the system clipboard
            cb = QApplication.clipboard()
            cb.setText(clipboard)
 
    def setData(self): 
        for ir in range(1, self.nrows):
            for ic in range(self.ncols):
                newitem = QTableWidgetItem(str(self.data[ir][ic]), QtCore.Qt.ItemIsSelectable)
                self.table.setItem(ir - 1, ic, newitem)
        self.table.setHorizontalHeaderLabels(self.data[0])