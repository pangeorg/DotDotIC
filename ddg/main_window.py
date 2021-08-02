
import os
from PyQt5.QtWidgets import QDialog, QMainWindow, QMenu, QAction, QTextEdit, QVBoxLayout
from PyQt5 import QtWidgets
from ddg import CentralWidget
from ddg.canvas import EditStyle, recentlyUsed
from ddg import __version__
from ddg.translator import translator

_TITLE_STRING = 'DotDotIC [v {}] - ECS / A2MAC1'.format(__version__)

class MainWindow(QMainWindow):
    def __init__(self, parent=None, screen=None):
        super().__init__(parent)
        self.setWindowTitle(_TITLE_STRING)
        self._centralWidget = CentralWidget()
        self.setCentralWidget(self._centralWidget)
        self.show()
        if screen:
            self.resize(int(screen.width() * .90), int(screen.height() * 0.90))
            self.move(int(screen.width() * .05) // 2, 0)

        self._createActions()
        self._createMenuBar()

        self._centralWidget.canvas.points_loaded.connect(self.update_title)
        self._centralWidget.canvas.points_saved.connect(self.update_title)
        self._centralWidget.pushButtonFolder.clicked.connect(self.select_folder)
        self._centralWidget.canvas.state_changed = False
    
    def _createMenuBar(self):
        import os
        from functools import partial
        menuBar = self.menuBar()
        # --- File menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.quickSaveAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.openAction)
        recentlyUsedMenu = QMenu("Recently Used", fileMenu)

        if len(recentlyUsed.files) == 0:
            action = QAction("No files", self)
            action.setEnabled(False)
            recentlyUsedMenu.addAction(action)
        else:
            for f in recentlyUsed.files:
                fname = os.path.basename(f)
                action = QAction(f, self)
                action.triggered.connect(partial(self.load_points, f))
                recentlyUsedMenu.addAction(action)

        fileMenu.addMenu(recentlyUsedMenu)
        fileMenu.addSeparator()
        fileMenu.addAction(self.exportCountsAction)
        fileMenu.addAction(self.exportDetailsAction)

        # --- Edit menu
        editMenu = QMenu("&Edit", self)
        menuBar.addMenu(editMenu)
        editMenu.addAction(self.editPointsAction)
        editMenu.addAction(self.editMeasureAction)

        # --- View
        viewMenu = QMenu("&View", self)
        menuBar.addMenu(viewMenu)
        viewMenu.addAction(self.showBomViewAction)

        # --- Help menu
        helpMenu = QMenu("&Help", self)
        menuBar.addMenu(helpMenu)
        helpMenu.addAction(self.infoAction)
        helpMenu.addAction(self.showControlsAction)

    def _createActions(self):
        self.saveAction = QAction("Save Project As...", self)
        self.saveAction.triggered.connect(self._centralWidget.point_widget.save)
        self.quickSaveAction = QAction("Save Project", self)
        self.quickSaveAction.triggered.connect(self._centralWidget.point_widget.quick_save)
        self.openAction = QAction("Open Project/Points", self)
        self.openAction.triggered.connect(self.load)
        # import metadata merge in load project ?
        self.exportCountsAction = QAction("Export to Text (csv)", self)
        self.exportCountsAction.triggered.connect(self._centralWidget.point_widget.export_counts)
        self.exportDetailsAction = QAction("Export detail images", self)
        self.exportDetailsAction.triggered.connect(self._centralWidget.point_widget.export_details)
        
        self.infoAction = QAction("Info", self)
        self.infoAction.triggered.connect(self.display_info)

        self.showControlsAction = QAction("Controls", self)
        self.showControlsAction.triggered.connect(self.display_controls)

        self.editPointsAction = QAction("Edit Counts", self)
        self.editPointsAction.setCheckable(True)
        self.editPointsAction.setChecked(True)
        self.editPointsAction.triggered.connect(self.set_edit_points)
        self._centralWidget.pointsToolButton.setDefaultAction(self.editPointsAction)

        self.editMeasureAction = QAction("Edit Measurements", self)
        self.editMeasureAction.setCheckable(True)
        self.editMeasureAction.setChecked(False)
        self.editMeasureAction.triggered.connect(self.set_edit_rects)
        self._centralWidget.rectsToolButton.setDefaultAction(self.editMeasureAction)

        self.showBomViewAction = QAction("BOM View", self)
        self.showBomViewAction.triggered.connect(self.showBomView)

    def showBomView(self):
        from ddg.table_view import TableView

        data = {'col1':['1','2','3','4'],
                'col2':['1','2','1','3'],
                'col3':['1','1','2','1']}

        data = self._centralWidget.canvas.prepare_export_counts()
        tw = TableView(data)
        tw.exec_()

    def load_points(self, filename):
        if self.check_save():
            if os.path.exists(filename):
                self._centralWidget.canvas.load_points(filename)
            else:
                message = filename + " not found"
                QtWidgets.QMessageBox.warning(self.parent(), 'Warning', message, QtWidgets.QMessageBox.Ok)

    def select_folder(self):
        if self.check_save():
            self._centralWidget.select_folder()        

    def display_info(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Information about DotDotIC " + __version__)
        dialog.resize(500, 500)
        textEdit = QTextEdit(dialog, readOnly=True)
        textEdit.setHtml(
            """
            <html>
                <body>
                    <article>
                        <h2> Info </h2>                            
                        <p> Version: {} </p>
                        <p> Bugeports: gstockinger@ecs-network.com </p>
                        <h2> Disclaimer </h2>
                        <p> DotDotIC is based in the fabulous DotDotGoose. </p>
                        <p> Please visit their website\nhttps://biodiversityinformatics.amnh.org/open_source/dotdotgoose ! </p>
                        <p></p>
                    </article>
                </body>
            </html>
        """.format(__version__))
        layout = QVBoxLayout()
        layout.addWidget(textEdit)
        dialog.setLayout(layout)
        _ = dialog.show()

    def display_controls(self):
        dialog = QDialog(self)
        dialog.setObjectName("Controls")
        dialog.setWindowTitle(translator.tr("Controls", "Controls"))
        dialog.resize(500, 500)
        textEdit = QTextEdit(dialog, readOnly=True)
        textEdit.setHtml(
            """
            <html>
                <body>
                    <article>
                        <h2> General </h2>                            
                        <p> There are two modes for counting or measuring which can be selected in the toolbar. </p>
                        <p> STRG + +             - Add component to current category    </p>
                        <p> G                    - Toggle Grid                          </p>
                        <p> D                    - Toggle Display                       </p>
                        <h2> Count Mode </h2>
                        <p> STRG + Right Click   - Add Count    </p>
                        <p> SHIFT + Drag         - Select Items </p>
                        <p> DEL (With Selection) - Delete Items </p>
                        <p></p>
                        <h2> Measure Mode </h2>
                        <p> C + Drag             - Calibrate Scale </p>
                        <p> M + Drag             - Measure         </p>
                        <p> SHIFT + Drag         - Select Items    </p>
                        <p> DEL (With Selection) - Delete Items    </p>
                    </article>
                </body>
            </html>
        """)
        layout = QVBoxLayout()
        layout.addWidget(textEdit)
        dialog.setLayout(layout)
        _ = dialog.show()
    
    def load(self):
        if self.check_save():
            self._centralWidget.point_widget.load()
            self.set_edit_points()

    def set_edit_points(self):
        self.editPointsAction.setChecked(True)
        self.editMeasureAction.setChecked(False)
        self._centralWidget.pointsToolButton.setChecked(True)
        self._centralWidget.rectsToolButton.setChecked(False)
        self._centralWidget.canvas.set_edit_style(EditStyle.POINTS)

    def set_edit_rects(self):
        self.editMeasureAction.setChecked(True)
        self.editPointsAction.setChecked(False)
        self._centralWidget.pointsToolButton.setChecked(False)
        self._centralWidget.rectsToolButton.setChecked(True)
        self._centralWidget.canvas.set_edit_style(EditStyle.RECTS)

    def update_title(self, survey_id, filename):
        self.setWindowTitle("{:} --- {:}".format(_TITLE_STRING, filename))

    def check_save(self):
        if not self._centralWidget.canvas.state_changed:
            return True
        msgBox = QtWidgets.QMessageBox()
        msgBox.setWindowTitle('Warning')
        msgBox.setText('You have unsaved changes')
        msgBox.setInformativeText('Do you want to continue?')
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.Ok)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        response = msgBox.exec()
        if response == QtWidgets.QMessageBox.Ok:
            return True
        return False

    def closeEvent(self, event):
        if self.check_save():
            event.accept()
        else:
            event.ignore()