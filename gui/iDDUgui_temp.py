# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\Marc\Documents\Projekte\iDDU\gui\iDDUgui.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
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
        self.groupBox_2 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 389, 291, 51))
        self.groupBox_2.setObjectName("groupBox_2")
        self.pushButton_StartDDU = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_StartDDU.setGeometry(QtCore.QRect(40, 20, 75, 23))
        self.pushButton_StartDDU.setObjectName("pushButton_StartDDU")
        self.pushButton_StopDDU = QtWidgets.QPushButton(self.groupBox_2)
        self.pushButton_StopDDU.setGeometry(QtCore.QRect(160, 20, 75, 23))
        self.pushButton_StopDDU.setObjectName("pushButton_StopDDU")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 10, 291, 171))
        self.groupBox_3.setObjectName("groupBox_3")
        self.spinBoxRaceLaps = QtWidgets.QSpinBox(self.groupBox_3)
        self.spinBoxRaceLaps.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.spinBoxRaceLaps.setMaximum(10000)
        self.spinBoxRaceLaps.setSingleStep(1)
        self.spinBoxRaceLaps.setObjectName("spinBoxRaceLaps")
        self.label_8 = QtWidgets.QLabel(self.groupBox_3)
        self.label_8.setGeometry(QtCore.QRect(20, 20, 81, 16))
        self.label_8.setObjectName("label_8")
        self.label_14 = QtWidgets.QLabel(self.groupBox_3)
        self.label_14.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_14.setObjectName("label_14")
        self.doubleSpinBox_P2PActivations = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_P2PActivations.setGeometry(QtCore.QRect(140, 100, 101, 22))
        self.doubleSpinBox_P2PActivations.setPrefix("")
        self.doubleSpinBox_P2PActivations.setSuffix("")
        self.doubleSpinBox_P2PActivations.setDecimals(0)
        self.doubleSpinBox_P2PActivations.setMaximum(1000.0)
        self.doubleSpinBox_P2PActivations.setSingleStep(1.0)
        self.doubleSpinBox_P2PActivations.setProperty("value", 12.0)
        self.doubleSpinBox_P2PActivations.setObjectName("doubleSpinBox_P2PActivations")
        self.doubleSpinBox_DRSActivations = QtWidgets.QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_DRSActivations.setGeometry(QtCore.QRect(140, 60, 101, 22))
        self.doubleSpinBox_DRSActivations.setPrefix("")
        self.doubleSpinBox_DRSActivations.setSuffix("")
        self.doubleSpinBox_DRSActivations.setDecimals(0)
        self.doubleSpinBox_DRSActivations.setMaximum(1000.0)
        self.doubleSpinBox_DRSActivations.setSingleStep(1.0)
        self.doubleSpinBox_DRSActivations.setProperty("value", 8.0)
        self.doubleSpinBox_DRSActivations.setObjectName("doubleSpinBox_DRSActivations")
        self.checkBox_MapHighlight = QtWidgets.QCheckBox(self.groupBox_3)
        self.checkBox_MapHighlight.setGeometry(QtCore.QRect(20, 140, 251, 17))
        self.checkBox_MapHighlight.setChecked(True)
        self.checkBox_MapHighlight.setObjectName("checkBox_MapHighlight")
        self.label_15 = QtWidgets.QLabel(self.groupBox_3)
        self.label_15.setGeometry(QtCore.QRect(20, 100, 101, 16))
        self.label_15.setObjectName("label_15")
        self.groupBox_4 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 190, 291, 91))
        self.groupBox_4.setObjectName("groupBox_4")
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_11.setObjectName("label_11")
        self.doubleSpinBox_PitStopDelta = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_PitStopDelta.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.doubleSpinBox_PitStopDelta.setPrefix("")
        self.doubleSpinBox_PitStopDelta.setSuffix("")
        self.doubleSpinBox_PitStopDelta.setDecimals(1)
        self.doubleSpinBox_PitStopDelta.setMaximum(1000.0)
        self.doubleSpinBox_PitStopDelta.setSingleStep(0.1)
        self.doubleSpinBox_PitStopDelta.setProperty("value", 60.0)
        self.doubleSpinBox_PitStopDelta.setObjectName("doubleSpinBox_PitStopDelta")
        self.doubleSpinBox_PitStopsRequired = QtWidgets.QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_PitStopsRequired.setGeometry(QtCore.QRect(140, 60, 101, 22))
        self.doubleSpinBox_PitStopsRequired.setPrefix("")
        self.doubleSpinBox_PitStopsRequired.setSuffix("")
        self.doubleSpinBox_PitStopsRequired.setDecimals(0)
        self.doubleSpinBox_PitStopsRequired.setMaximum(1000.0)
        self.doubleSpinBox_PitStopsRequired.setSingleStep(1.0)
        self.doubleSpinBox_PitStopsRequired.setProperty("value", 1.0)
        self.doubleSpinBox_PitStopsRequired.setObjectName("doubleSpinBox_PitStopsRequired")
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(20, 20, 81, 16))
        self.label_10.setObjectName("label_10")
        self.groupBox_5 = QtWidgets.QGroupBox(self.tabGeneral)
        self.groupBox_5.setGeometry(QtCore.QRect(10, 290, 291, 91))
        self.groupBox_5.setObjectName("groupBox_5")
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setGeometry(QtCore.QRect(20, 60, 101, 16))
        self.label_13.setObjectName("label_13")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setGeometry(QtCore.QRect(20, 20, 101, 16))
        self.label_12.setObjectName("label_12")
        self.doubleSpinBox_JokerLapDelta = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_JokerLapDelta.setGeometry(QtCore.QRect(140, 20, 101, 22))
        self.doubleSpinBox_JokerLapDelta.setPrefix("")
        self.doubleSpinBox_JokerLapDelta.setSuffix("")
        self.doubleSpinBox_JokerLapDelta.setDecimals(0)
        self.doubleSpinBox_JokerLapDelta.setMaximum(1000.0)
        self.doubleSpinBox_JokerLapDelta.setSingleStep(0.1)
        self.doubleSpinBox_JokerLapDelta.setProperty("value", 2.0)
        self.doubleSpinBox_JokerLapDelta.setObjectName("doubleSpinBox_JokerLapDelta")
        self.doubleSpinBox_JokerLapsRequired = QtWidgets.QDoubleSpinBox(self.groupBox_5)
        self.doubleSpinBox_JokerLapsRequired.setGeometry(QtCore.QRect(140, 60, 101, 22))
        self.doubleSpinBox_JokerLapsRequired.setPrefix("")
        self.doubleSpinBox_JokerLapsRequired.setSuffix("")
        self.doubleSpinBox_JokerLapsRequired.setDecimals(0)
        self.doubleSpinBox_JokerLapsRequired.setMaximum(1000.0)
        self.doubleSpinBox_JokerLapsRequired.setSingleStep(1.0)
        self.doubleSpinBox_JokerLapsRequired.setProperty("value", 1.0)
        self.doubleSpinBox_JokerLapsRequired.setObjectName("doubleSpinBox_JokerLapsRequired")
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
        self.saveButton = QtWidgets.QPushButton(self.groupBox)
        self.saveButton.setGeometry(QtCore.QRect(230, 20, 41, 23))
        self.saveButton.setObjectName("saveButton")
        self.openButton = QtWidgets.QPushButton(self.groupBox)
        self.openButton.setGeometry(QtCore.QRect(170, 20, 41, 23))
        self.openButton.setObjectName("openButton")
        self.tabWidget.addTab(self.tabUpshiftTone, "")
        self.tabDebug = QtWidgets.QWidget()
        self.tabDebug.setObjectName("tabDebug")
        self.pushButton = QtWidgets.QPushButton(self.tabDebug)
        self.pushButton.setGeometry(QtCore.QRect(230, 430, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.lineEdit = QtWidgets.QLineEdit(self.tabDebug)
        self.lineEdit.setGeometry(QtCore.QRect(10, 430, 211, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.textEdit = QtWidgets.QTextEdit(self.tabDebug)
        self.textEdit.setGeometry(QtCore.QRect(10, 10, 291, 411))
        self.textEdit.setObjectName("textEdit")
        self.tabWidget.addTab(self.tabDebug, "")

        self.retranslateUi(Form)
        self.tabWidget.setCurrentIndex(0)
        self.comboBox.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.groupBox_2.setTitle(_translate("Form", "DDU"))
        self.pushButton_StartDDU.setText(_translate("Form", "Start DDU"))
        self.pushButton_StopDDU.setText(_translate("Form", "Stop DDU"))
        self.groupBox_3.setTitle(_translate("Form", "General"))
        self.label_8.setText(_translate("Form", "Race Laps"))
        self.label_14.setText(_translate("Form", "DRS Activations"))
        self.checkBox_MapHighlight.setText(_translate("Form", "activate Delta on Map"))
        self.label_15.setText(_translate("Form", "P2P Activations"))
        self.groupBox_4.setTitle(_translate("Form", "Pit Stop"))
        self.label_11.setText(_translate("Form", "Required Pit Stops"))
        self.label_10.setText(_translate("Form", "Pit Stop Delta"))
        self.groupBox_5.setTitle(_translate("Form", "RallyX"))
        self.label_13.setText(_translate("Form", "Required Joker Laps"))
        self.label_12.setText(_translate("Form", "Joker Lap Delta"))
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
        self.label_9.setText(_translate("Form", "Upshift RPM Source"))
        self.checkBox_UpshiftTone.setText(_translate("Form", "activate Upshift Tone"))
        self.saveButton.setText(_translate("Form", "Save"))
        self.openButton.setText(_translate("Form", "Load"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabUpshiftTone), _translate("Form", "Upshift Tone"))
        self.pushButton.setText(_translate("Form", "PushButton"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tabDebug), _translate("Form", "Debug"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
