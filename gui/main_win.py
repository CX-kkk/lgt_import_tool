# -*- coding: utf-8 -*-
import os
import sys
from functools import partial

from Qt import QtWidgets, _loadUi
from hz.naming_api import NamingAPI
from lgt_import_tool.core import assign_shader, core, utils
from lgt_import_tool.gui import basic_gui


class PreviewWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)

        ui_file = os.path.join(os.path.dirname(__file__), 'win.ui')
        _loadUi(ui_file, self)

        self.setWindowTitle('Lighting import tool')
        self.current_file_path = core.get_current_scene_file()
        # self.switch_bool = self.get_radio_button_options(self.QFrame_opt) == 'from_version'
        self.init_ui()
        self.init_layout()
        self.init_connectiond()
        self.get_abc_from_version()
        self.get_lay_abc_from_version()

    def init_ui(self):
        self.set_version_combobox(self.comboBox_anim_version, 'anim')
        self.set_version_combobox(self.comboBox_lay_version, 'layout')

    def set_version_combobox(self, combo_box, step):
        all_versions = utils.get_all_published_versions(self.current_file_path, step)
        combo_box.clear()
        combo_box.addItems(all_versions)

    @staticmethod
    def get_radio_button_options(frame_widget):
        for child in frame_widget.children():
            if not isinstance(child, QtWidgets.QRadioButton):
                continue
            if child.isChecked():
                return str(child.objectName())

    @staticmethod
    def get_check_box_options(check_box):
        return check_box.isChecked()

    @staticmethod
    def get_combobox_options(combobox):
        return combobox.currentText()

    @staticmethod
    def get_line_edit_options(line_edit):
        return line_edit.text()

    def widget_enable(self):
        from_anim = self.checkBox_from_anim.isChecked()
        self.Qwidget_from_anim.setEnabled(from_anim)
        from_layout = self.checkBox_from_layout.isChecked()
        self.Qwidget_from_layout.setEnabled(from_layout)

    def load_mode_opt(self, QFrame, QWidget_from_version, QWidget_from_path):
        self.switch_bool = self.get_radio_button_options(QFrame).endswith('from_version')
        QWidget_from_version.setEnabled(self.switch_bool)
        QWidget_from_path.setEnabled(not self.switch_bool)

    def init_layout(self):
        self.listWidget_anim_abc = basic_gui.ListWidget()
        self.verticalLayout_anim_items.addWidget(self.listWidget_anim_abc)
        self.listWidget_layout_abc = basic_gui.ListWidget()
        self.verticalLayout_lauout_items.addWidget(self.listWidget_layout_abc)

    def init_connectiond(self):
        self.checkBox_from_anim.clicked.connect(self.widget_enable)
        self.checkBox_from_layout.clicked.connect(self.widget_enable)
        self.radioButton_from_version.clicked.connect(partial(self.load_mode_opt, self.QFrame_opt,
                                                              self.QWidget_from_version,
                                                              self.QWidget_from_path))
        self.radioButton_from_path.clicked.connect(partial(self.load_mode_opt, self.QFrame_opt,
                                                           self.QWidget_from_version,
                                                           self.QWidget_from_path))
        self.radioButton_lay_from_version.clicked.connect(partial(self.load_mode_opt, self.QFrame_lay_opt,
                                                                  self.QWidget_lay_from_version,
                                                                  self.QWidget_lay_from_path))
        self.radioButton_lay_from_path.clicked.connect(partial(self.load_mode_opt, self.QFrame_lay_opt,
                                                               self.QWidget_lay_from_version,
                                                               self.QWidget_lay_from_path))
        self.comboBox_anim_version.currentIndexChanged.connect(self.get_abc_from_version)
        self.lineEdit_anim_path.textEdited.connect(self.get_anim_abc_from_path)
        self.comboBox_lay_version.currentIndexChanged.connect(self.get_lay_abc_from_version)
        self.lineEdit_lay_path.textEdited.connect(self.get_lay_abc_from_path)
        self.pushButton_apply.clicked.connect(self.run)
        self.pushButton_cancle.clicked.connect(self.close)

    def get_abc(self, full_path, listWidget_abc):
        listWidget_abc.clear_item()
        abc_list = filter(lambda x: os.path.splitext(x)[-1] == '.abc', os.listdir(full_path))
        rig_info_file = os.path.join(full_path, 'rigging_info.json')
        if os.path.isfile(rig_info_file):
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
                listWidget_abc.add_item(basic_gui.MotionItem(abc, enable=True), metadata)

    def get_abc_from_version(self):
        version = self.get_combobox_options(self.comboBox_anim_version)
        file_path = utils.get_certain_version(self.current_file_path, version, 'anim')
        full_path = os.path.dirname(file_path)
        if os.path.exists(full_path):
            self.get_abc(full_path, self.listWidget_anim_abc)
        print 'Get abc cache from: ', full_path

    def get_lay_abc_from_version(self):
        version = self.get_combobox_options(self.comboBox_lay_version)
        file_path = utils.get_certain_version(self.current_file_path, version, 'layout')
        full_path = os.path.dirname(file_path)
        if os.path.exists(full_path):
            self.get_abc(full_path, self.listWidget_layout_abc)
        print 'Get abc cache from: ', full_path

    def get_anim_abc_from_path(self):
        full_path = self.get_line_edit_options(self.lineEdit_anim_path)
        if os.path.exists(full_path):
            self.get_abc(full_path, self.listWidget_anim_abc)

    def get_lay_abc_from_path(self):
        full_path = self.get_line_edit_options(self.lineEdit_lay_path)
        if os.path.exists(full_path):
            self.get_abc(full_path, self.listWidget_layout_abc)

    def run(self):
        print 'run'
        abc_widgets = []
        if self.checkBox_from_anim.isChecked():
            abc_widgets.append(self.listWidget_anim_abc)
        if self.checkBox_from_layout.isChecked():
            abc_widgets.append(self.listWidget_layout_abc)
        num = 0
        for listWidget_abc in abc_widgets:
            for each in listWidget_abc:
                metadata = each.metadata
                load_abc = each.widget.abc_checked
                load_texture = each.widget.texture_checked
                assign_shader.main(metadata.get('abc_path'),
                                   metadata.get('json_path'),
                                   metadata.get('shader_path'),
                                   metadata.get('namespace')+'_{}'.format(num), load_abc=load_abc,
                                   load_texture=load_texture)
                num += 1


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    aa = PreviewWidget()
    aa.show()
    sys.exit(app.exec_())
