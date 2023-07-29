
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QAction,
    QToolBar,
    QLineEdit,
    QLabel,
    QMenu,
    QCheckBox,
    QSplitter,
) 
from PyQt5.QtCore import Qt, QEvent, QPoint, QSize
from PyQt5.QtGui import QFont, QTextCursor


from pathlib import Path
import sys
from zipfile import ZipFile, ZIP_DEFLATED
import os

from custom_classes import *

class CreateWindow(QWidget):

    def __init__(self, location):
        super().__init__()
        self.location = location
        self.setWindowTitle("Create File")
        self.font = QFont("Terminal",30)
        self.setFixedSize(500,200)
        layout = QVBoxLayout()

        self.name = QLineEdit()

        self.name.setPlaceholderText("Enter File Name")
        self.name.setFont(self.font)
        self.name.installEventFilter(self)
        layout.addWidget(self.name)

        self.is_dir = QCheckBox("Is this a folder")
        self.is_dir.setFont(self.font)
        layout.addWidget(self.is_dir)

        self.label = QPushButton("create file")
        self.label.setFont(self.font)
        self.label.clicked.connect(self.create_file)
        layout.addWidget(self.label)
        self.setLayout(layout)

    def eventFilter(self,source, event):
        return super().eventFilter(source,event)

    def create_file(self):
        if self.is_dir.isChecked():
            os.makedirs(self.location + self.name.text())
        else:
            f = open(self.location + self.name.text(), "x")

        btn = window.make_button(self.location + self.name.text())
        i = 0
        for i,name in enumerate(window.titles):
            if name.lower() > btn.text().lower():
                break
        window.lay.insertWidget(i,btn)
        window.titles.insert(i,btn.text())
        self.close()

class ErrorWindow(QWidget):

    def __init__(self, error):
        super().__init__()
        self.setWindowTitle("ERROR")
        self.font = QFont("Terminal",30)
        self.setFixedSize(500,200)
        layout = QVBoxLayout()

        self.title = QLabel(error)
        self.title.setFont(self.font)
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.label = QPushButton("I UNDERSTAND")
        self.label.setFont(self.font)
        self.label.clicked.connect(self.c)
        layout.addWidget(self.label)
        self.setLayout(layout)
    
    def c(self):
        self.close()
