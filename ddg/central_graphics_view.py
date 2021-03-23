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
from PyQt5 import QtWidgets, QtCore


class CentralGraphicsView(QtWidgets.QGraphicsView):
    add_point = QtCore.pyqtSignal(QtCore.QPointF)
    display_pointer_coordinates = QtCore.pyqtSignal(QtCore.QPointF)
    drop_complete = QtCore.pyqtSignal(list)
    region_selected = QtCore.pyqtSignal(QtCore.QRectF)
    scale_selected = QtCore.pyqtSignal(QtCore.QRectF) # signal for measuring pixels vs mm
    measure_area = QtCore.pyqtSignal(QtCore.QRectF) # signal for measuring pixels vs mm
    delete_selection = QtCore.pyqtSignal()
    relabel_selection = QtCore.pyqtSignal()
    toggle_points = QtCore.pyqtSignal()
    toggle_grid = QtCore.pyqtSignal()
    switch_class = QtCore.pyqtSignal(int)

    def __init__(self, parent=None):
        QtWidgets.QGraphicsView.__init__(self, parent)
        self.setMouseTracking(True)
        self.setAcceptDrops(True)
        self.shift = False
        self.ctrl = False
        self.alt = False
        self.set_scale = False
        self.m = False
        self.delay = 0
        self.setViewportUpdateMode(0)

    def enterEvent(self, event):
        self.setFocus()

    def dragEnterEvent(self, event):
        event.setAccepted(True)

    def dragMoveEvent(self, event):
        pass

    def dropEvent(self, event):
        if len(event.mimeData().urls()) > 0:
            self.drop_complete.emit(event.mimeData().urls())

    def image_loaded(self, directory, file_name):
        self.resetTransform()
        self.fitInView(self.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
        self.setSceneRect(self.scene().itemsBoundingRect())

    def keyPressEvent(self, event):
        key = event.key()
        if event.key() == QtCore.Qt.Key_Alt:
            self.alt = True
        elif event.key() == QtCore.Qt.Key_Control:
            self.ctrl = True
        elif event.key() == QtCore.Qt.Key_Shift:
            self.shift = True
        elif event.key() == QtCore.Qt.Key_E:
            self.set_scale = True
        elif event.key() == QtCore.Qt.Key_M:
           self.m = True
        elif event.key() == QtCore.Qt.Key_Delete or event.key() == QtCore.Qt.Key_Backspace:
            self.delete_selection.emit()
        elif event.key() == QtCore.Qt.Key_R:
            self.relabel_selection.emit()
        elif event.key() == QtCore.Qt.Key_D:
            self.toggle_points.emit()
        elif event.key() == QtCore.Qt.Key_G:
            self.toggle_grid.emit()
        elif event.key() == QtCore.Qt.Key_1:
            self.switch_class.emit(0)
        elif event.key() == QtCore.Qt.Key_2:
            self.switch_class.emit(1)
        elif event.key() == QtCore.Qt.Key_3:
            self.switch_class.emit(2)
        elif event.key() == QtCore.Qt.Key_4:
            self.switch_class.emit(3)
        elif event.key() == QtCore.Qt.Key_5:
            self.switch_class.emit(4)
        elif event.key() == QtCore.Qt.Key_6:
            self.switch_class.emit(5)
        elif event.key() == QtCore.Qt.Key_7:
            self.switch_class.emit(6)
        elif event.key() == QtCore.Qt.Key_8:
            self.switch_class.emit(7)
        elif event.key() == QtCore.Qt.Key_9:
            self.switch_class.emit(8)
        elif event.key() == QtCore.Qt.Key_0:
            self.switch_class.emit(9)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key_Alt:
            self.alt = False
        elif event.key() == QtCore.Qt.Key_Control:
            self.ctrl = False
        elif event.key() == QtCore.Qt.Key_Shift:
            self.shift = False
        elif event.key() == QtCore.Qt.Key_E:
            self.set_scale = False
        elif event.key() == QtCore.Qt.Key_M:
            self.m = False

    def mouseMoveEvent(self, event):
        QtWidgets.QGraphicsView.mouseMoveEvent(self, event)
        self.display_pointer_coordinates.emit(self.mapToScene(event.pos()))

    def mousePressEvent(self, event):
        if self.ctrl:
            self.add_point.emit(self.mapToScene(event.pos()))
        elif self.shift or self.set_scale or self.m:
            self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
        else:
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            QtWidgets.QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.dragMode() == QtWidgets.QGraphicsView.RubberBandDrag:
            rect = self.rubberBandRect()
            if self.shift:
                self.region_selected.emit(self.mapToScene(rect).boundingRect())
                self.shift = False
            elif self.set_scale:
                self.scale_selected.emit(self.mapToScene(rect).boundingRect())
                self.set_scale = False
            elif self.m:
                self.measure_area.emit(self.mapToScene(rect).boundingRect())
                self.m = False
            QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)
        self.setDragMode(QtWidgets.QGraphicsView.NoDrag)

    def resizeEvent(self, event):
        self.resize_image()

    def resize_image(self):
        vsb = self.verticalScrollBar().isVisible()
        hsb = self.horizontalScrollBar().isVisible()
        if not (vsb or hsb):
            self.fitInView(self.scene().itemsBoundingRect(), QtCore.Qt.KeepAspectRatio)
            self.setSceneRect(self.scene().itemsBoundingRect())

    def wheelEvent(self, event):
        if len(self.scene().items()) > 0:
            if event.angleDelta().y() > 0:
                self.zoom_in()
            else:
                self.zoom_out()

    def zoom_in(self):
        self.scale(1.1, 1.1)
        # Fix for MacOS and PyQt5 > v5.10
        self.repaint()

    def zoom_out(self):
        self.scale(0.9, 0.9)
        # Fix for MacOS and PyQt5 > v5.10
        self.repaint()
