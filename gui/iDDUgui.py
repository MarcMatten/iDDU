# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'iDDUgui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys, pygame, time

class Stream(QtCore.QObject):
    newText = QtCore.pyqtSignal(str)

    def write(self, text):
        self.newText.emit(str(text))

class iDDUgui(object):
    def setupUi(self, Form, db):
        self.db = db
        self.Form = Form
        Form.setObjectName("Form")
        Form.resize(320, 480)
        self.tabWidget = QtWidgets.QTabWidget(Form)
        self.tabWidget.setGeometry(QtCore.QRect(0, 0, 320, 480))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy)
        self.tabWidget.setObjectName("tabWidget")
        self.tabGeneral = QtWidgets.QWidget()
        self.tabGeneral.setObjectName("tabGeneral")
        self.label_8 = QtWidgets.QLabel(self.tabGeneral)
        self.label_8.setGeometry(QtCore.QRect(40, 20, 81, 16))
        self.label_8.setObjectName("label_8")
        self.label_10 = QtWidgets.QLabel(self.tabGeneral)
        self.label_10.setGeometry(QtCore.QRect(40, 50, 81, 16))
        self.label_10.setObjectName("label_10")
        self.doubleSpinBox_PitStopDelta = QtWidgets.QDoubleSpinBox(self.tabGeneral)
        self.doubleSpinBox_PitStopDelta.setGeometry(QtCore.QRect(160, 50, 101, 22))
        self.doubleSpinBox_PitStopDelta.setPrefix("")
        self.doubleSpinBox_PitStopDelta.setSuffix("")
        self.doubleSpinBox_PitStopDelta.setDecimals(1)
        self.doubleSpinBox_PitStopDelta.setMaximum(1000.0)
        self.doubleSpinBox_PitStopDelta.setSingleStep(0.1)
        self.doubleSpinBox_PitStopDelta.setProperty("value", 60.0)
        self.doubleSpinBox_PitStopDelta.setObjectName("doubleSpinBox_PitStopDelta")
        self.spinBoxRaceLaps = QtWidgets.QSpinBox(self.tabGeneral)
        self.spinBoxRaceLaps.setGeometry(QtCore.QRect(160, 20, 101, 22))
        self.spinBoxRaceLaps.setMaximum(10000)
        self.spinBoxRaceLaps.setSingleStep(1)
        self.spinBoxRaceLaps.setObjectName("spinBoxRaceLaps")
        self.tabWidget.addTab(self.tabGeneral, "")
        self.tabUpshiftTone = QtWidgets.QWidget()
        self.tabUpshiftTone.setObjectName("tabUpshiftTone")
        self.groupBox = QtWidgets.QGroupBox(self.tabUpshiftTone)
        self.groupBox.setGeometry(QtCore.QRect(10, 0, 291, 451))
        self.groupBox.setObjectName("groupBox")
        self.groupBox_Gear1 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear1.setGeometry(QtCore.QRect(10, 90, 271, 51))
        self.groupBox_Gear1.setObjectName("groupBox_Gear1")
        self.spinBox_Gear1 = QtWidgets.QSpinBox(self.groupBox_Gear1)
        self.spinBox_Gear1.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear1.setMinimum(4000)
        self.spinBox_Gear1.setMaximum(20000)
        self.spinBox_Gear1.setSingleStep(10)
        self.spinBox_Gear1.setObjectName("spinBox_Gear1")
        self.label = QtWidgets.QLabel(self.groupBox_Gear1)
        self.label.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label.setObjectName("label")
        self.checkBox_Gear1 = QtWidgets.QCheckBox(self.groupBox_Gear1)
        self.checkBox_Gear1.setEnabled(True)
        self.checkBox_Gear1.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear1.setAcceptDrops(False)
        self.checkBox_Gear1.setChecked(True)
        self.checkBox_Gear1.setObjectName("checkBox_Gear1")
        self.groupBox_Gear2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear2.setGeometry(QtCore.QRect(10, 140, 271, 51))
        self.groupBox_Gear2.setObjectName("groupBox_Gear2")
        self.spinBox_Gear2 = QtWidgets.QSpinBox(self.groupBox_Gear2)
        self.spinBox_Gear2.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear2.setMinimum(4000)
        self.spinBox_Gear2.setMaximum(20000)
        self.spinBox_Gear2.setSingleStep(10)
        self.spinBox_Gear2.setObjectName("spinBox_Gear2")
        self.label_2 = QtWidgets.QLabel(self.groupBox_Gear2)
        self.label_2.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_2.setObjectName("label_2")
        self.checkBox_Gear2 = QtWidgets.QCheckBox(self.groupBox_Gear2)
        self.checkBox_Gear2.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear2.setChecked(True)
        self.checkBox_Gear2.setObjectName("checkBox_Gear2")
        self.groupBox_Gear3 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear3.setGeometry(QtCore.QRect(10, 190, 271, 51))
        self.groupBox_Gear3.setObjectName("groupBox_Gear3")
        self.spinBox_Gear3 = QtWidgets.QSpinBox(self.groupBox_Gear3)
        self.spinBox_Gear3.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear3.setMinimum(4000)
        self.spinBox_Gear3.setMaximum(20000)
        self.spinBox_Gear3.setSingleStep(10)
        self.spinBox_Gear3.setObjectName("spinBox_Gear3")
        self.label_3 = QtWidgets.QLabel(self.groupBox_Gear3)
        self.label_3.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_3.setObjectName("label_3")
        self.checkBox_Gear3 = QtWidgets.QCheckBox(self.groupBox_Gear3)
        self.checkBox_Gear3.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear3.setChecked(True)
        self.checkBox_Gear3.setObjectName("checkBox_Gear3")
        self.groupBox_Gear4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear4.setGeometry(QtCore.QRect(10, 240, 271, 51))
        self.groupBox_Gear4.setObjectName("groupBox_Gear4")
        self.spinBox_Gear4 = QtWidgets.QSpinBox(self.groupBox_Gear4)
        self.spinBox_Gear4.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear4.setMinimum(4000)
        self.spinBox_Gear4.setMaximum(20000)
        self.spinBox_Gear4.setSingleStep(10)
        self.spinBox_Gear4.setObjectName("spinBox_Gear4")
        self.label_4 = QtWidgets.QLabel(self.groupBox_Gear4)
        self.label_4.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_4.setObjectName("label_4")
        self.checkBox_Gear4 = QtWidgets.QCheckBox(self.groupBox_Gear4)
        self.checkBox_Gear4.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear4.setChecked(True)
        self.checkBox_Gear4.setObjectName("checkBox_Gear4")
        self.groupBox_Gear2_4 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear2_4.setGeometry(QtCore.QRect(10, 290, 271, 51))
        self.groupBox_Gear2_4.setObjectName("groupBox_Gear2_4")
        self.spinBox_Gear5 = QtWidgets.QSpinBox(self.groupBox_Gear2_4)
        self.spinBox_Gear5.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear5.setMinimum(4000)
        self.spinBox_Gear5.setMaximum(20000)
        self.spinBox_Gear5.setSingleStep(10)
        self.spinBox_Gear5.setObjectName("spinBox_Gear5")
        self.label_5 = QtWidgets.QLabel(self.groupBox_Gear2_4)
        self.label_5.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_5.setObjectName("label_5")
        self.checkBox_Gear5 = QtWidgets.QCheckBox(self.groupBox_Gear2_4)
        self.checkBox_Gear5.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear5.setChecked(True)
        self.checkBox_Gear5.setObjectName("checkBox_Gear5")
        self.groupBox_Gear6 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear6.setGeometry(QtCore.QRect(10, 340, 271, 51))
        self.groupBox_Gear6.setObjectName("groupBox_Gear6")
        self.spinBox_Gear6 = QtWidgets.QSpinBox(self.groupBox_Gear6)
        self.spinBox_Gear6.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear6.setMinimum(4000)
        self.spinBox_Gear6.setMaximum(20000)
        self.spinBox_Gear6.setSingleStep(10)
        self.spinBox_Gear6.setObjectName("spinBox_Gear6")
        self.label_6 = QtWidgets.QLabel(self.groupBox_Gear6)
        self.label_6.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_6.setObjectName("label_6")
        self.checkBox_Gear6 = QtWidgets.QCheckBox(self.groupBox_Gear6)
        self.checkBox_Gear6.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear6.setObjectName("checkBox_Gear6")
        self.groupBox_Gear7 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_Gear7.setGeometry(QtCore.QRect(10, 390, 271, 51))
        self.groupBox_Gear7.setObjectName("groupBox_Gear7")
        self.spinBox_Gear7 = QtWidgets.QSpinBox(self.groupBox_Gear7)
        self.spinBox_Gear7.setGeometry(QtCore.QRect(20, 20, 71, 22))
        self.spinBox_Gear7.setMinimum(4000)
        self.spinBox_Gear7.setMaximum(20000)
        self.spinBox_Gear7.setSingleStep(10)
        self.spinBox_Gear7.setObjectName("spinBox_Gear7")
        self.label_7 = QtWidgets.QLabel(self.groupBox_Gear7)
        self.label_7.setGeometry(QtCore.QRect(110, 20, 46, 22))
        self.label_7.setObjectName("label_7")
        self.checkBox_Gear7 = QtWidgets.QCheckBox(self.groupBox_Gear7)
        self.checkBox_Gear7.setGeometry(QtCore.QRect(170, 20, 51, 22))
        self.checkBox_Gear7.setObjectName("checkBox_Gear7")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(150, 60, 131, 22))
        self.comboBox.setMaxVisibleItems(5)
        self.comboBox.setCurrentIndex(2)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.label_9 = QtWidgets.QLabel(self.groupBox)
        self.label_9.setGeometry(QtCore.QRect(20, 60, 101, 22))
        self.label_9.setObjectName("label_9")
        self.checkBox_UpshiftTone = QtWidgets.QCheckBox(self.groupBox)
        self.checkBox_UpshiftTone.setGeometry(QtCore.QRect(20, 30, 251, 17))
        self.checkBox_UpshiftTone.setChecked(True)
        self.checkBox_UpshiftTone.setObjectName("checkBox_UpshiftTone")
        self.tabWidget.addTab(self.tabUpshiftTone, "")
        self.tabDebug = QtWidgets.QWidget()
        self.tabDebug.setObjectName("tabDebug")
        self.pushButtonInvoke = QtWidgets.QPushButton(self.tabDebug)
        self.pushButtonInvoke.setGeometry(QtCore.QRect(230, 430, 75, 23))
        self.pushButtonInvoke.setObjectName("pushButtonInvoke")
        self.lineEditInvoke = QtWidgets.QLineEdit(self.tabDebug)
        self.lineEditInvoke.setGeometry(QtCore.QRect(10, 430, 211, 20))
        self.lineEditInvoke.setObjectName("lineEditInvoke")
        self.textEdit = QtWidgets.QTextEdit(self.tabDebug)
        self.textEdit.setGeometry(QtCore.QRect(10, 10, 291, 411))
        self.textEdit.setObjectName("textEdit")
        self.tabWidget.addTab(self.tabDebug, "")

        # sys.stdout = Stream(newText=self.onUpdateText)

        self.spinBoxRaceLaps.setValue(self.db.RaceLaps)
        self.doubleSpinBox_PitStopDelta.setValue(self.db.PitStopDelta)

        self.spinBoxRaceLaps.valueChanged.connect(self.assignRaceLaps)
        self.doubleSpinBox_PitStopDelta.valueChanged.connect(self.assignPitStopDelta)

        self.checkBox_UpshiftTone.stateChanged.connect(self.EnableShiftTone)
        self.comboBox.currentIndexChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear1.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear1.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear2.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear2.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear3.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear3.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear4.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear4.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear5.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear5.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear6.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear6.stateChanged.connect(self.UpshiftStrategy)
        self.spinBox_Gear7.valueChanged.connect(self.UpshiftStrategy)
        self.checkBox_Gear7.stateChanged.connect(self.UpshiftStrategy)
        self.pushButtonInvoke.clicked.connect(self.InvokeUserCommand)

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Form)
        self.UpshiftStrategy()

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "iDDU"))
        self.label_8.setText(_translate("Form", "Race Laps"))
        self.label_10.setText(_translate("Form", "Pit Stop Delta"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabGeneral), _translate("Form", "General"))
        self.groupBox.setTitle(_translate("Form", "Upshift RPM"))
        self.groupBox_Gear1.setTitle(_translate("Form", "Gear 1"))
        self.label.setText(_translate("Form", "RPM"))
        self.checkBox_Gear1.setText(_translate("Form", "active"))
        self.groupBox_Gear2.setTitle(_translate("Form", "Gear 2"))
        self.label_2.setText(_translate("Form", "RPM"))
        self.checkBox_Gear2.setText(_translate("Form", "active"))
        self.groupBox_Gear3.setTitle(_translate("Form", "Gear 3"))
        self.label_3.setText(_translate("Form", "RPM"))
        self.checkBox_Gear3.setText(_translate("Form", "active"))
        self.groupBox_Gear4.setTitle(_translate("Form", "Gear 4"))
        self.label_4.setText(_translate("Form", "RPM"))
        self.checkBox_Gear4.setText(_translate("Form", "active"))
        self.groupBox_Gear2_4.setTitle(_translate("Form", "Gear 5"))
        self.label_5.setText(_translate("Form", "RPM"))
        self.checkBox_Gear5.setText(_translate("Form", "active"))
        self.groupBox_Gear6.setTitle(_translate("Form", "Gear 6"))
        self.label_6.setText(_translate("Form", "RPM"))
        self.checkBox_Gear6.setText(_translate("Form", "active"))
        self.groupBox_Gear7.setTitle(_translate("Form", "Gear 7"))
        self.label_7.setText(_translate("Form", "RPM"))
        self.checkBox_Gear7.setText(_translate("Form", "active"))
        self.comboBox.setItemText(0, _translate("Form", "iRacing First RPM"))
        self.comboBox.setItemText(1, _translate("Form", "iRacing Shift RPM"))
        self.comboBox.setItemText(2, _translate("Form", "iRacing Last RPM"))
        self.comboBox.setItemText(3, _translate("Form", "iRacing Blink RPM"))
        self.comboBox.setItemText(4, _translate("Form", "User defined"))
        self.comboBox.setCurrentIndex(1)
        self.label_9.setText(_translate("Form", "Upshift RPM Source"))
        self.checkBox_UpshiftTone.setText(_translate("Form", "activate Upshift Tone"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabUpshiftTone), _translate("Form", "Upshift Tone"))
        self.pushButtonInvoke.setText(_translate("Form", "Invoke"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDebug), _translate("Form", "Debug"))

    def assignRaceLaps(self):
        self.db.LapsToGo = self.spinBoxRaceLaps.value()
        self.db.RaceLaps = self.spinBoxRaceLaps.value()
        self.retranslateUi(self.Form)

    def assignPitStopDelta(self):
        self.db.PitStopDelta = self.doubleSpinBox_PitStopDelta.value()
        self.retranslateUi(self.Form)

    def UpshiftStrategy(self):
        self.db.UpshiftStrategy = self.comboBox.currentIndex()
        self.db.UserShiftRPM = [self.spinBox_Gear1.value(), self.spinBox_Gear2.value(), self.spinBox_Gear3.value(), self.spinBox_Gear4.value(), self.spinBox_Gear5.value(), self.spinBox_Gear6.value(), self.spinBox_Gear7.value()]
        self.db.UserShiftFlag = [self.checkBox_Gear1.isChecked(), self.checkBox_Gear2.isChecked(), self.checkBox_Gear3.isChecked(), self.checkBox_Gear4.isChecked(), self.checkBox_Gear5.isChecked(), self.checkBox_Gear6.isChecked(), self.checkBox_Gear7.isChecked()]
        #print(self.db.UpshiftStrategy)
        #print(self.db.UserShiftRPM)
        #print(self.db.UserShiftFlag)
        self.retranslateUi(self.Form)

    def EnableShiftTone(self):
        self.db.ShiftToneEnabled = self.checkBox_UpshiftTone.isChecked()
        self.retranslateUi(self.Form)

    def InvokeUserCommand(self):
        try:
            cmd = self.lineEditInvoke.text()
            print(">> " + cmd)
            print(eval(cmd))
        except:
            print('User command not working!')

    def __init__(self, db):
        import sys
        app = QtWidgets.QApplication(sys.argv)
        Form = QtWidgets.QWidget()
        Form.setFixedSize(320, 480)
        # ui = iDDUgui()
        self.setupUi(Form, db)
        sys.stdout = Stream(newText=self.onUpdateText)
        sys.stderr = Stream(newText=self.onUpdateText)
        Form.show()
        sys.exit(app.exec_())

    def onUpdateText(self, text):
        cursor = self.textEdit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.textEdit.setTextCursor(cursor)
        self.textEdit.ensureCursorVisible()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def exitFcn(self, event):
        print("event")
        time.sleep(10)
        reply = QtGui.QMessageBox.question(self, 'Message',
            "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
