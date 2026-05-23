# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'untitledBEQXQz.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (QHBoxLayout, QLineEdit, QPushButton, QTextBrowser, QVBoxLayout, QWidget)
import config
import resource

class Ui_Form(object):
    def setupUi(self, Form: QWidget):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(604, 456)
        self.verticalLayout = QVBoxLayout(Form)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.textBrowser = QTextBrowser(Form)
        self.textBrowser.setObjectName(u"textBrowser")

        self.verticalLayout.addWidget(self.textBrowser)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.lineEdit = QLineEdit(Form)
        self.lineEdit.setObjectName(u"lineEdit")

        self.horizontalLayout.addWidget(self.lineEdit)

        self.pushButton = QPushButton(Form)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout.addWidget(self.pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", config.window_title.chat_ui, None))
        self.lineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"Post the message", None))
        self.pushButton.setText(QCoreApplication.translate("Form", u"Send", None))
        Form.setWindowIcon(QIcon(config.datafile + "logo.png"))
    # retranslateUi

