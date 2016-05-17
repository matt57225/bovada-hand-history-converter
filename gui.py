#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2016 matt57225
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Form implementation generated from reading ui file 'gui.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName(_fromUtf8("Form"))
        Form.resize(500, 315)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setMinimumSize(QtCore.QSize(500, 315))
        Form.setMaximumSize(QtCore.QSize(500, 315))
        self.gridLayoutForm = QtGui.QGridLayout(Form)
        self.gridLayoutForm.setObjectName(_fromUtf8("gridLayoutForm"))
        self.gridLayout_1 = QtGui.QGridLayout()
        self.gridLayout_1.setObjectName(_fromUtf8("gridLayout_1"))
        self.statusLabel = QtGui.QLabel(Form)
        self.statusLabel.setMinimumSize(QtCore.QSize(0, 25))
        self.statusLabel.setObjectName(_fromUtf8("statusLabel"))
        self.gridLayout_1.addWidget(self.statusLabel, 10, 0, 1, 1)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setContentsMargins(-1, 15, -1, -1)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.moveDirLabel = QtGui.QLabel(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.moveDirLabel.sizePolicy().hasHeightForWidth())
        self.moveDirLabel.setSizePolicy(sizePolicy)
        self.moveDirLabel.setMinimumSize(QtCore.QSize(140, 0))
        self.moveDirLabel.setObjectName(_fromUtf8("moveDirLabel"))
        self.horizontalLayout_3.addWidget(self.moveDirLabel)
        self.moveDirCheckBox = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.moveDirCheckBox.sizePolicy().hasHeightForWidth())
        self.moveDirCheckBox.setSizePolicy(sizePolicy)
        self.moveDirCheckBox.setChecked(True)
        self.moveDirCheckBox.setObjectName(_fromUtf8("moveDirCheckBox"))
        self.horizontalLayout_3.addWidget(self.moveDirCheckBox)
        self.gridLayout_1.addLayout(self.horizontalLayout_3, 7, 0, 1, 1)
        self.moveDirText = QtGui.QLineEdit(Form)
        self.moveDirText.setObjectName(_fromUtf8("moveDirText"))
        self.gridLayout_1.addWidget(self.moveDirText, 8, 0, 1, 1)
        self.inputDirText = QtGui.QLineEdit(Form)
        self.inputDirText.setObjectName(_fromUtf8("inputDirText"))
        self.gridLayout_1.addWidget(self.inputDirText, 4, 0, 1, 1)
        self.inputDirLabel = QtGui.QLabel(Form)
        self.inputDirLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.inputDirLabel.setObjectName(_fromUtf8("inputDirLabel"))
        self.gridLayout_1.addWidget(self.inputDirLabel, 3, 0, 1, 1)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(-1, 10, -1, -1)
        self.horizontalLayout_4.setSpacing(15)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.runButton = QtGui.QPushButton(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.runButton.sizePolicy().hasHeightForWidth())
        self.runButton.setSizePolicy(sizePolicy)
        self.runButton.setMinimumSize(QtCore.QSize(0, 30))
        self.runButton.setCursor(QtGui.QCursor(QtCore.Qt.ArrowCursor))
        self.runButton.setObjectName(_fromUtf8("runButton"))
        self.horizontalLayout_4.addWidget(self.runButton)
        self.progressBar = QtGui.QProgressBar(Form)
        self.progressBar.setEnabled(True)
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout_4.addWidget(self.progressBar)
        self.gridLayout_1.addLayout(self.horizontalLayout_4, 9, 0, 1, 1)
        self.horizontalLayout_1 = QtGui.QHBoxLayout()
        self.horizontalLayout_1.setObjectName(_fromUtf8("horizontalLayout_1"))
        self.showKnownCheckBox = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.showKnownCheckBox.sizePolicy().hasHeightForWidth())
        self.showKnownCheckBox.setSizePolicy(sizePolicy)
        self.showKnownCheckBox.setObjectName(_fromUtf8("showKnownCheckBox"))
        self.horizontalLayout_1.addWidget(self.showKnownCheckBox)
        self.fastFoldCheckBox = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.fastFoldCheckBox.sizePolicy().hasHeightForWidth())
        self.fastFoldCheckBox.setSizePolicy(sizePolicy)
        self.fastFoldCheckBox.setObjectName(_fromUtf8("fastFoldCheckBox"))
        self.horizontalLayout_1.addWidget(self.fastFoldCheckBox)
        self.gridLayout_1.addLayout(self.horizontalLayout_1, 0, 0, 1, 1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.stbmsCheckBox = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.stbmsCheckBox.sizePolicy().hasHeightForWidth())
        self.stbmsCheckBox.setSizePolicy(sizePolicy)
        self.stbmsCheckBox.setObjectName(_fromUtf8("stbmsCheckBox"))
        self.horizontalLayout_2.addWidget(self.stbmsCheckBox)
        self.saveErrorsCheckBox = QtGui.QCheckBox(Form)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.saveErrorsCheckBox.sizePolicy().hasHeightForWidth())
        self.saveErrorsCheckBox.setSizePolicy(sizePolicy)
        self.saveErrorsCheckBox.setObjectName(_fromUtf8("saveErrorsCheckBox"))
        self.horizontalLayout_2.addWidget(self.saveErrorsCheckBox)
        self.gridLayout_1.addLayout(self.horizontalLayout_2, 2, 0, 1, 1)
        self.outputDirText = QtGui.QLineEdit(Form)
        self.outputDirText.setObjectName(_fromUtf8("outputDirText"))
        self.gridLayout_1.addWidget(self.outputDirText, 6, 0, 1, 1)
        self.outputDirLabel = QtGui.QLabel(Form)
        self.outputDirLabel.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft)
        self.outputDirLabel.setObjectName(_fromUtf8("outputDirLabel"))
        self.gridLayout_1.addWidget(self.outputDirLabel, 5, 0, 1, 1)
        self.inputDirButton = QtGui.QToolButton(Form)
        self.inputDirButton.setObjectName(_fromUtf8("inputDirButton"))
        self.gridLayout_1.addWidget(self.inputDirButton, 4, 1, 1, 1)
        self.outputDirButton = QtGui.QToolButton(Form)
        self.outputDirButton.setObjectName(_fromUtf8("outputDirButton"))
        self.gridLayout_1.addWidget(self.outputDirButton, 6, 1, 1, 1)
        self.moveDirButton = QtGui.QToolButton(Form)
        self.moveDirButton.setObjectName(_fromUtf8("moveDirButton"))
        self.gridLayout_1.addWidget(self.moveDirButton, 8, 1, 1, 1)
        spacerItem = QtGui.QSpacerItem(40, 5, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout_1.addItem(spacerItem, 1, 0, 1, 1)
        self.gridLayoutForm.addLayout(self.gridLayout_1, 0, 0, 1, 1)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)
        Form.setTabOrder(self.inputDirText, self.outputDirText)
        Form.setTabOrder(self.outputDirText, self.moveDirText)
        Form.setTabOrder(self.moveDirText, self.moveDirCheckBox)
        Form.setTabOrder(self.moveDirCheckBox, self.runButton)
        Form.setTabOrder(self.runButton, self.showKnownCheckBox)
        Form.setTabOrder(self.showKnownCheckBox, self.stbmsCheckBox)
        Form.setTabOrder(self.stbmsCheckBox, self.fastFoldCheckBox)
        Form.setTabOrder(self.fastFoldCheckBox, self.saveErrorsCheckBox)
        Form.setTabOrder(self.saveErrorsCheckBox, self.inputDirButton)
        Form.setTabOrder(self.inputDirButton, self.outputDirButton)
        Form.setTabOrder(self.outputDirButton, self.moveDirButton)

    def retranslateUi(self, Form):
        Form.setWindowTitle(_translate("Form", "HHConverter", None))
        self.statusLabel.setText(_translate("Form", "Ready", None))
        self.moveDirLabel.setText(_translate("Form", "Move Processed Directory", None))
        self.moveDirCheckBox.setText(_translate("Form", "Enable", None))
        self.inputDirLabel.setText(_translate("Form", "Input Directory", None))
        self.runButton.setText(_translate("Form", "Run", None))
        self.showKnownCheckBox.setText(_translate("Form", "Show known hole cards", None))
        self.fastFoldCheckBox.setText(_translate("Form", "Convert Zone to fast fold", None))
        self.stbmsCheckBox.setText(_translate("Form", "Separate HU, 6-max, and FR", None))
        self.saveErrorsCheckBox.setText(_translate("Form", "Save errors to file", None))
        self.outputDirLabel.setText(_translate("Form", "Output Directory", None))
        self.inputDirButton.setText(_translate("Form", "...", None))
        self.outputDirButton.setText(_translate("Form", "...", None))
        self.moveDirButton.setText(_translate("Form", "...", None))
