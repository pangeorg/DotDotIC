# -*- coding: utf-8 -*-
#
# DotDotGoose
# Author: Peter Ersts (ersts@amnh.org)
#
# --------------------------------------------------------------------------
#
# This file is part of the DotDotGoose application.
# DotDotGoose was forked from the Neural Network Image Classifier (Nenetic).
#
# DotDotGoose is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# DotDotGoose is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------
import os
import sys
from PyQt5 import QtCore, QtWidgets, QtGui, uic

from ddg import Canvas
from ddg.canvas import Scale, manufacturer_names, package_names
from ddg import PointWidget
from ddg.fields import BoxText, LineText
from ddg.ui.central_widget_ui import Ui_CentralWidget as CLASS_DIALOG

# if getattr(sys, 'frozen', False):
#     from ddg.ui.central_widget_ui import Ui_CentralWidget as CLASS_DIALOG
# else:
#     bundle_dir = os.path.dirname(__file__)
#     CLASS_DIALOG, _ = uic.loadUiType(os.path.join(bundle_dir, 'ui', 'central_widget.ui'))


class CentralWidget(QtWidgets.QDialog, CLASS_DIALOG):

    load_custom_data = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self)
        self.setupUi(self)
        self.canvas = Canvas()

        self.point_widget = PointWidget(self.canvas, self)
        self.findChild(QtWidgets.QFrame, 'framePointWidget').layout().addWidget(self.point_widget)
        self.point_widget.hide_custom_fields.connect(self.hide_custom_fields)
        self.point_widget.saving.connect(self.display_quick_save)
        self.point_widget.class_selection_changed.connect(self.display_attributes)

        self.save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("Ctrl+S")), self)  # quick save using Ctrl+S
        self.save_shortcut.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.save_shortcut.activated.connect(self.point_widget.quick_save)

        self.up_arrow = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Up), self)
        self.up_arrow.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.up_arrow.activated.connect(self.point_widget.previous)

        self.down_arrow = QtWidgets.QShortcut(QtGui.QKeySequence(QtCore.Qt.Key_Down), self)
        self.down_arrow.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.down_arrow.activated.connect(self.point_widget.next)

        # same as arrows but conventient for right handed people
        self.up_arrow = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("W")), self)
        self.up_arrow.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.up_arrow.activated.connect(self.point_widget.previous)

        self.down_arrow = QtWidgets.QShortcut(QtGui.QKeySequence(self.tr("S")), self)
        self.down_arrow.setContext(QtCore.Qt.WidgetWithChildrenShortcut)
        self.down_arrow.activated.connect(self.point_widget.next)

        self.graphicsView.setScene(self.canvas)
        self.graphicsView.drop_complete.connect(self.canvas.load)
        self.graphicsView.region_selected.connect(self.canvas.select_points)
        self.graphicsView.delete_selection.connect(self.canvas.delete_selected_points)
        self.graphicsView.clear_selection.connect(self.canvas.clear_selection)
        self.graphicsView.relabel_selection.connect(self.canvas.relabel_selected_points)
        self.graphicsView.measure_area.connect(self.canvas.measure_area)
        self.graphicsView.toggle_points.connect(self.point_widget.checkBoxDisplayPoints.toggle)
        self.graphicsView.toggle_grid.connect(self.point_widget.checkBoxDisplayGrid.toggle)
        self.graphicsView.scale_selected.connect(self.set_scale)
        # self.graphicsView.switch_class.connect(self.point_widget.set_active_class)

        self.graphicsView.add_point.connect(self.canvas.add_point)
        self.graphicsView.display_pointer_coordinates.connect(self.display_pointer_coordinates)
        self.canvas.image_loaded.connect(self.graphicsView.image_loaded)
        self.canvas.directory_set.connect(self.display_working_directory)

        # Image data fields
        self.canvas.image_loaded.connect(self.display_coordinates)
        self.canvas.image_loaded.connect(self.display_attributes)
        self.canvas.fields_updated.connect(self.display_attributes)
        self.lineEditX.textEdited.connect(self.update_coordinates)
        self.lineEditY.textEdited.connect(self.update_coordinates)
        self.lineEditX.setDisabled(True)
        self.lineEditY.setDisabled(True)

        self.lineEdit_attributes = {}
        self.lineEdit_attributes["Marking"] = self.lineEdit_marking
        self.lineEdit_attributes["Partnumber"] = self.lineEdit_partnumber
        self.lineEdit_attributes["Manufacturer"] = self.lineEdit_manufacturer
        self.lineEdit_attributes["Package"] = self.lineEdit_package
        self.lineEdit_attributes["Length"] = self.lineEdit_length
        self.lineEdit_attributes["Width"] = self.lineEdit_width
        self.lineEdit_attributes["Height"] = self.lineEdit_height
        for k, lineEdit in self.lineEdit_attributes.items():
            lineEdit.textEdited.connect(self.update_attributes)
            lineEdit.setDisabled(True)

        package_completer = QtWidgets.QCompleter(package_names)
        self.lineEdit_package.setCompleter(package_completer)

        manufacturer_completer = QtWidgets.QCompleter(manufacturer_names)
        self.lineEdit_manufacturer.setCompleter(manufacturer_completer)

        self.pushButtonFolder.clicked.connect(self.select_folder)
        self.pushButtonZoomOut.clicked.connect(self.graphicsView.zoom_out)
        self.pushButtonZoomIn.clicked.connect(self.graphicsView.zoom_in)

        self.quick_save_frame = QtWidgets.QFrame(self.graphicsView)
        self.quick_save_frame.setStyleSheet("QFrame { background: #4caf50;color: #FFF;font-weight: bold}")
        self.quick_save_frame.setLayout(QtWidgets.QHBoxLayout())
        self.quick_save_frame.layout().addWidget(QtWidgets.QLabel('Saving...'))
        self.quick_save_frame.setGeometry(3, 3, 100, 35)
        self.quick_save_frame.hide()

    def display_pointer_coordinates(self, point):
        img = self.canvas.current_image_name
        image_scale = self.canvas.image_scale.get(img, Scale())
        scale = image_scale.scale
        left = image_scale.left
        top = image_scale.top
        unit = image_scale.unit
        text = "{:.1f}, {:.1f} {}".format(int(point.x())*scale - left, int(point.y())*scale - top, unit)
        self.posLabel.setText(text)

    def set_scale(self, rect):
        mm, ok = QtWidgets.QInputDialog.getInt(self, 'Set scale', 'Enter Length (x-axis) in mm')
        if ok:
            self.canvas.set_scale(mm, rect)

    def resizeEvent(self, theEvent):
        self.graphicsView.resize_image()

    def display_coordinates(self, directory, image):
        if self.canvas.current_image_name is None:
            self.lineEditX.setDisabled(True)
            self.lineEditY.setDisabled(True)
        else:
            self.lineEditX.setDisabled(False)
            self.lineEditY.setDisabled(False)
        if image in self.canvas.coordinates:
            self.lineEditX.setText(self.canvas.coordinates[image]['x'])
            self.lineEditY.setText(self.canvas.coordinates[image]['y'])
        else:
            self.lineEditX.setText('')
            self.lineEditY.setText('')

    def display_attributes(self):
        if self.canvas.current_class_name is None or self.canvas.current_image_name is None:
            for _, lineEdit in self.lineEdit_attributes.items():
                lineEdit.setText("")
                lineEdit.setDisabled(True)
        else:
            for k, lineEdit in self.lineEdit_attributes.items():
                lineEdit.setDisabled(False)
                value = self.canvas.class_attributes[self.canvas.current_class_name][k]
                if k == "Packages":
                    if value not in package_names:
                        package_names.append(value)
                        package_names.sort()
                        self.lineEdit_package.setCompleter(QtWidgets.QCompleter(package_names))
                elif k == "Manufacturer":
                    if value not in manufacturer_names:
                        manufacturer_names.append(value)
                        manufacturer_names.sort()
                        self.lineEdit_manufacturer.setCompleter(QtWidgets.QCompleter(manufacturer_names))
                lineEdit.setText(value)
                
    def display_working_directory(self, directory):
        self.labelWorkingDirectory.setText(directory)

    def display_quick_save(self):
        self.quick_save_frame.show()
        QtCore.QTimer.singleShot(500, self.quick_save_frame.hide)

    def hide_custom_fields(self, hide):
        if hide is True:
            self.frameCustomField.hide()
        else:
            self.frameCustomField.show()

    def select_folder(self):
        name = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select image folder', self.canvas.directory)
        if name != '':
            self.canvas.load([QtCore.QUrl('file:{}'.format(name))])

    def update_coordinates(self, text):
        x = self.lineEditX.text()
        y = self.lineEditY.text()
        self.canvas.save_coordinates(x, y)
        
    def update_attributes(self, text):
        for k, lineEdit in self.lineEdit_attributes.items():
            value = lineEdit.text()
            self.canvas.set_component_attribute(k, value)