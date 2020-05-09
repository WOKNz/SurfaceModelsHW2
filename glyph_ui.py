# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'glyph_view.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(775, 600)
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.splitter = QtWidgets.QSplitter(self.centralwidget)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame_load = QtWidgets.QHBoxLayout()
        self.frame_load.setContentsMargins(0, 8, 0, 8)
        self.frame_load.setObjectName("frame_load")
        self.label_info = QtWidgets.QLabel(self.frame)
        self.label_info.setObjectName("label_info")
        self.frame_load.addWidget(self.label_info)
        self.label_status = QtWidgets.QLabel(self.frame)
        self.label_status.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_status.setObjectName("label_status")
        self.frame_load.addWidget(self.label_status)
        self.button_load = QtWidgets.QPushButton(self.frame)
        self.button_load.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.button_load.setCheckable(False)
        self.button_load.setObjectName("button_load")
        self.frame_load.addWidget(self.button_load)
        self.verticalLayout.addLayout(self.frame_load)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.vtk_panel = QtWidgets.QFrame(self.splitter)
        self.vtk_panel.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.vtk_panel.setFrameShadow(QtWidgets.QFrame.Raised)
        self.vtk_panel.setObjectName("vtk_panel")
        self.horizontalLayout.addWidget(self.splitter)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 775, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "GlyphViewer"))
        self.label_info.setText(_translate("MainWindow", "Load Points (.xyz/.pts)"))
        self.label_status.setText(_translate("MainWindow", "Something Loaded!"))
        self.button_load.setText(_translate("MainWindow", "Load file"))
