# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'design.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(1026, 701)
        MainWindow.setMinimumSize(QtCore.QSize(1026, 701))
        MainWindow.setMaximumSize(QtCore.QSize(1026, 701))
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.feed_label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.feed_label.sizePolicy().hasHeightForWidth())
        self.feed_label.setSizePolicy(sizePolicy)
        self.feed_label.setScaledContents(True)
        self.feed_label.setObjectName(_fromUtf8("feed_label"))
        self.horizontalLayout_2.addWidget(self.feed_label)
        self.guidance_label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.guidance_label.sizePolicy().hasHeightForWidth())
        self.guidance_label.setSizePolicy(sizePolicy)
        self.guidance_label.setScaledContents(True)
        self.guidance_label.setObjectName(_fromUtf8("guidance_label"))
        self.horizontalLayout_2.addWidget(self.guidance_label)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.instruction_label = QtGui.QLabel(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.instruction_label.sizePolicy().hasHeightForWidth())
        self.instruction_label.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(24)
        font.setBold(True)
        font.setWeight(75)
        self.instruction_label.setFont(font)
        self.instruction_label.setTextFormat(QtCore.Qt.RichText)
        self.instruction_label.setScaledContents(False)
        self.instruction_label.setAlignment(QtCore.Qt.AlignCenter)
        self.instruction_label.setWordWrap(True)
        self.instruction_label.setObjectName(_fromUtf8("instruction_label"))
        self.verticalLayout_2.addWidget(self.instruction_label)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.feed_label.setText(_translate("MainWindow", "Image 1", None))
        self.guidance_label.setText(_translate("MainWindow", "Image 2", None))
        self.instruction_label.setText(_translate("MainWindow", "Instruction", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

