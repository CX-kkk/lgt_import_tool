# -*- coding: utf-8 -*-
import importlib
import os
import sys

from Qt import QtCore, QtWidgets, _loadUi, QtGui
from hz.naming_api import NamingAPI
import basic_gui
from core import assign_shader, core, utils


class PreviewWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)

        ui_file = os.path.join(os.path.dirname(__file__), 'win.ui')
        _loadUi(ui_file, self)

        self.setWindowTitle('test Tool')
        self.current_file_path = core.get_current_scene_file()
        self.switch_bool = self.get_radio_button_options(self.QFrame_opt) == 'from_version'
        self.init_ui()
        self.init_layout()
        self.init_connectiond()
        # test_path = 'X:/pipelinernd_rnd-0000/zzz_dev/test_shot/3d/anim/_publish/v005'
        # self.lineEdit_path.setText(test_path)

    def init_ui(self):
        self.set_version_combobox()

    def set_version_combobox(self):
        all_versions = utils.get_all_published_versions(self.current_file_path, 'anim')
        self.comboBox_version.clear()
        self.comboBox_version.addItems(all_versions)

    @staticmethod
    def get_radio_button_options(frame_widget):
        for child in frame_widget.children():
            if not isinstance(child, QtWidgets.QRadioButton):
                continue
            if child.isChecked():
                return str(child.objectName()).replace('radioButton_', '')

    @staticmethod
    def get_check_box_options(check_box):
        return check_box.isChecked()

    @staticmethod
    def get_combobox_options(combobox):
        return combobox.currentText()

    @staticmethod
    def get_line_edit_options(line_edit):
        return line_edit.text()

    def load_opt(self):
        self.switch_bool = self.get_radio_button_options(self.QFrame_opt) == 'from_version'
        self.QWidget_from_version.setEnabled(self.switch_bool)
        self.QWidget_from_path.setEnabled(not self.switch_bool)

        if self.switch_bool:
            version = self.get_combobox_options(self.comboBox_version)
            # full_path = os.path.join('/sw/...', version)
            print 'from_version'

    def get_abc(self, full_path):
        self.listWidget_abc.clear_item()
        abc_list = filter(lambda x: os.path.splitext(x)[-1] == '.abc', os.listdir(full_path))
        rigging_dict = utils.read_in_json(os.path.join(full_path, 'rigging_info.json'))
        for abc in abc_list:
            abc_path = os.path.join(str(full_path), abc.encode())
            asset_name = abc.rsplit('.', 1)[0].rsplit('_', 1)[-1]
            rigging_path = rigging_dict[asset_name].values()[0]
            naming = NamingAPI.parser(rigging_path)
            naming.task = 'shd'
            latest_shd_path = os.path.dirname(naming.get_latest_version())
            metadata = {'abc_name': abc, 'abc_path': abc_path,
                        'namespace': abc.rsplit('.', 1)[0],
                        'asset_name': asset_name,
                        'shader_path': os.path.join(latest_shd_path, '{}.ma'.format(asset_name)),
                        'json_path': os.path.join(latest_shd_path, '{}.json'.format(asset_name))
                        }
            self.listWidget_abc.add_item(basic_gui.MotionItem(abc, enable=True), metadata)

    def get_abc_from_version(self):
        version = self.get_combobox_options(self.comboBox_version)
        file_path = utils.get_certain_version(self.current_file_path, version, 'anim')
        full_path = os.path.dirname(file_path)
        # self.lineEdit_path.setText(full_path)
        if os.path.exists(full_path):
            self.get_abc(full_path)
        print 'Get abc cache from: ', full_path

    def get_abc_from_path(self):
        full_path = self.get_line_edit_options(self.lineEdit_path)
        if os.path.exists(full_path):
            print self.get_abc(full_path)

    def init_layout(self):
        self.listWidget_abc = basic_gui.ListWidget()
        self.verticalLayout_items.addWidget(self.listWidget_abc)
        # self.setLayout(self.verticalLayout_publish.parent())

    def run(self):
        print 'run'
        for each in self.listWidget_abc:
            metadata = each.metadata
            load_abc = each.widget.abc_checked
            load_texture = each.widget.texture_checked
            assign_shader.main(metadata.get('abc_path'), metadata.get('json_path'), metadata.get('shader_path'),
                               metadata.get('namespace'), load_abc=load_abc, load_texture=load_texture)

    def init_connectiond(self):
        self.radioButton_from_version.clicked.connect(self.load_opt)
        self.radioButton_from_path.clicked.connect(self.load_opt)
        self.comboBox_version.currentIndexChanged.connect(self.get_abc_from_version)
        self.lineEdit_path.textEdited.connect(self.get_abc_from_path)
        self.pushButton_apply.clicked.connect(self.run)
        self.pushButton_cancle.clicked.connect(self.close)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    aa = PreviewWidget()
    aa.show()
    sys.exit(app.exec_())