# -*- coding: utf-8 -*-
from collections import namedtuple

from Qt import QtCore, QtWidgets, _loadUi, QtGui


WidgetData = namedtuple("WidgetData", ["widget", "metadata"])


class ListWidget(QtWidgets.QWidget):
    def __init__(self, height=30):
        super(ListWidget, self).__init__()

        self.height = height
        self.data = list()
        self.pool = QtWidgets.QListWidget()
        self.pool.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

        self.init_ui()

    def __getitem__(self, index):
        clean_data = list()
        for item in self.data:
            if item.widget:
                clean_data.append(item)
        return clean_data[index]

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(self.pool)

        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def clear_item(self):
        self.data = list()
        self.pool.clear()

    def add_item(self, item, metadata=None, height=None):
        assert isinstance(item, QtWidgets.QWidget)
        list_item = QtWidgets.QListWidgetItem()
        self.data.append(WidgetData(item, metadata))
        qsize = QtCore.QSize()
        height = height if height else self.height
        qsize.setHeight(height)
        list_item.setSizeHint(qsize)
        self.pool.addItem(list_item)
        self.pool.setItemWidget(list_item, self.data[-1].widget)

class MotionItem(QtWidgets.QWidget):
    """
    The item widget of QListWidget in motion group box.
    Used to toggle motion info exporter of each asset in layout scene.
    """
    def __init__(self, name, enable=True, abc_option=True, texture_option=True):
        super(MotionItem, self).__init__()

        self.label = QtWidgets.QLabel(name)
        self.checkbox = QtWidgets.QCheckBox("Import")

        self.abc_box = QtWidgets.QCheckBox('Abc')
        self.texture_box = QtWidgets.QCheckBox('Texture')
        for each_box in [self.abc_box, self.texture_box]:
            each_box.setDisabled(True)
        self.abc_option = abc_option
        self.texture_option = texture_option

        if enable:
            self.checkbox.setChecked(True)
            for each_box in [self.abc_box, self.texture_box]:
                each_box.setDisabled(False)
                each_box.setChecked(True)
        else:
            self.label.setDisabled(False)

        self.init_ui()

    def __nonzero__(self):
        return self.checkbox.isChecked()

    @property
    def name(self):
        return str(self.label.text())

    @property
    def abc_checked(self):
        return self.abc_box.isChecked()

    @property
    def texture_checked(self):
        return self.texture_box.isChecked()

    def checkbox_state_changed(self):
        if self.checkbox.isChecked():
            for each_box in [self.abc_box, self.texture_box]:
                each_box.setDisabled(False)
        else:
            for each_box in [self.abc_box, self.texture_box]:
                each_box.setDisabled(True)
                each_box.setChecked(False)

    def init_ui(self):
        self.checkbox.clicked.connect(self.label.setEnabled)
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.checkbox)
        if self.abc_option:
            layout.addWidget(self.abc_box)
        if self.texture_option:
            layout.addWidget(self.texture_box)

        self.setLayout(layout)