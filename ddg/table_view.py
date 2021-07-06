from PyQt5.QtWidgets import QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView

class TableView(QDialog):
    def __init__(self, data, *args):
        QDialog.__init__(self, *args)
        self.verticalLayout = QVBoxLayout(self)
        self.table = QTableWidget(parent=self)
        self.nrows = len(data)
        self.ncols = len(data[0])
        print(self.nrows, self.ncols)
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
 
    def setData(self): 
        for ir in range(1, self.nrows):
            for ic in range(self.ncols):
                newitem = QTableWidgetItem(self.data[ir][ic])
                self.table.setItem(ir - 1, ic, newitem)
        self.table.setHorizontalHeaderLabels(self.data[0])