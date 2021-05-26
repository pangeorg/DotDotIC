# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\ddg\ui\central_widget.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_CentralWidget(object):
    def setupUi(self, CentralWidget):
        CentralWidget.setObjectName("CentralWidget")
        CentralWidget.resize(1192, 526)
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(CentralWidget)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.framePointWidget = QtWidgets.QFrame(CentralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.framePointWidget.sizePolicy().hasHeightForWidth())
        self.framePointWidget.setSizePolicy(sizePolicy)
        self.framePointWidget.setMinimumSize(QtCore.QSize(350, 0))
        self.framePointWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.framePointWidget.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.framePointWidget.setFrameShadow(QtWidgets.QFrame.Plain)
        self.framePointWidget.setLineWidth(0)
        self.framePointWidget.setObjectName("framePointWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.framePointWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5.addWidget(self.framePointWidget)
        self.frameCenter = QtWidgets.QFrame(CentralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(3)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameCenter.sizePolicy().hasHeightForWidth())
        self.frameCenter.setSizePolicy(sizePolicy)
        self.frameCenter.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameCenter.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCenter.setObjectName("frameCenter")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.frameCenter)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.toolLayout = QtWidgets.QVBoxLayout()
        self.toolLayout.setContentsMargins(0, -1, -1, -1)
        self.toolLayout.setObjectName("toolLayout")
        self.verticalLayout_4.addLayout(self.toolLayout)
        self.graphicsView = CentralGraphicsView(self.frameCenter)
        self.graphicsView.setObjectName("graphicsView")
        self.verticalLayout_4.addWidget(self.graphicsView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, 4, -1, -1)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonFolder = QtWidgets.QPushButton(self.frameCenter)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icons/folder.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonFolder.setIcon(icon)
        self.pushButtonFolder.setIconSize(QtCore.QSize(24, 24))
        self.pushButtonFolder.setObjectName("pushButtonFolder")
        self.horizontalLayout.addWidget(self.pushButtonFolder)
        self.label_3 = QtWidgets.QLabel(self.frameCenter)
        self.label_3.setObjectName("label_3")
        self.horizontalLayout.addWidget(self.label_3)
        self.labelWorkingDirectory = QtWidgets.QLabel(self.frameCenter)
        self.labelWorkingDirectory.setText("")
        self.labelWorkingDirectory.setObjectName("labelWorkingDirectory")
        self.horizontalLayout.addWidget(self.labelWorkingDirectory)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.pushButtonZoomIn = QtWidgets.QPushButton(self.frameCenter)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/icons/zoom_in.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonZoomIn.setIcon(icon1)
        self.pushButtonZoomIn.setIconSize(QtCore.QSize(24, 24))
        self.pushButtonZoomIn.setObjectName("pushButtonZoomIn")
        self.horizontalLayout.addWidget(self.pushButtonZoomIn)
        self.pushButtonZoomOut = QtWidgets.QPushButton(self.frameCenter)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/icons/zoom_out.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButtonZoomOut.setIcon(icon2)
        self.pushButtonZoomOut.setIconSize(QtCore.QSize(24, 24))
        self.pushButtonZoomOut.setObjectName("pushButtonZoomOut")
        self.horizontalLayout.addWidget(self.pushButtonZoomOut)
        self.verticalLayout_4.addLayout(self.horizontalLayout)
        self.horizontalLayout_5.addWidget(self.frameCenter)
        self.frameCustomField = QtWidgets.QFrame(CentralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(1)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frameCustomField.sizePolicy().hasHeightForWidth())
        self.frameCustomField.setSizePolicy(sizePolicy)
        self.frameCustomField.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frameCustomField.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCustomField.setObjectName("frameCustomField")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frameCustomField)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupBoxImageData = QtWidgets.QGroupBox(self.frameCustomField)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxImageData.sizePolicy().hasHeightForWidth())
        self.groupBoxImageData.setSizePolicy(sizePolicy)
        self.groupBoxImageData.setMinimumSize(QtCore.QSize(0, 0))
        self.groupBoxImageData.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBoxImageData.setObjectName("groupBoxImageData")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBoxImageData)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout_2.addLayout(self.gridLayout_2)
        self.groupBoxCustomFields = QtWidgets.QGroupBox(self.groupBoxImageData)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxCustomFields.sizePolicy().hasHeightForWidth())
        self.groupBoxCustomFields.setSizePolicy(sizePolicy)
        self.groupBoxCustomFields.setObjectName("groupBoxCustomFields")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.groupBoxCustomFields)
        self.verticalLayout_3.setContentsMargins(8, -1, 8, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setContentsMargins(0, -1, -1, -1)
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(5)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout_3.addLayout(self.gridLayout)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.verticalLayout_2.addWidget(self.groupBoxCustomFields)
        self.groupBoxPosition = QtWidgets.QGroupBox(self.groupBoxImageData)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBoxPosition.sizePolicy().hasHeightForWidth())
        self.groupBoxPosition.setSizePolicy(sizePolicy)
        self.groupBoxPosition.setTitle("")
        self.groupBoxPosition.setObjectName("groupBoxPosition")
        self.posLabel = QtWidgets.QLabel(self.groupBoxPosition)
        self.posLabel.setGeometry(QtCore.QRect(2, -4, 191, 20))
        self.posLabel.setObjectName("posLabel")
        self.verticalLayout_2.addWidget(self.groupBoxPosition)
        self.verticalLayout_5.addWidget(self.groupBoxImageData)
        self.horizontalLayout_5.addWidget(self.frameCustomField)

        self.retranslateUi(CentralWidget)
        QtCore.QMetaObject.connectSlotsByName(CentralWidget)
        CentralWidget.setTabOrder(self.pushButtonFolder, self.pushButtonZoomIn)
        CentralWidget.setTabOrder(self.pushButtonZoomIn, self.pushButtonZoomOut)
        CentralWidget.setTabOrder(self.pushButtonZoomOut, self.graphicsView)

    def retranslateUi(self, CentralWidget):
        _translate = QtCore.QCoreApplication.translate
        CentralWidget.setWindowTitle(_translate("CentralWidget", "Form"))
        self.pushButtonFolder.setToolTip(_translate("CentralWidget", "Load folder of images."))
        self.pushButtonFolder.setText(_translate("CentralWidget", "Open Directory"))
        self.label_3.setText(_translate("CentralWidget", "Working Directory:"))
        self.pushButtonZoomIn.setToolTip(_translate("CentralWidget", "Zoom in."))
        self.pushButtonZoomIn.setText(_translate("CentralWidget", "+"))
        self.pushButtonZoomOut.setToolTip(_translate("CentralWidget", "Zoom out."))
        self.pushButtonZoomOut.setText(_translate("CentralWidget", "-"))
        self.groupBoxImageData.setTitle(_translate("CentralWidget", "PCB Data"))
        self.groupBoxCustomFields.setTitle(_translate("CentralWidget", "Component details"))
        self.posLabel.setText(_translate("CentralWidget", "0,0"))
from ddg.central_graphics_view import CentralGraphicsView
