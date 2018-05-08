# -*- coding: utf-8 -*-
import importlib
import os
import sys

from Qt import QtCore, QtWidgets, _loadUi, QtGui
import basic_gui
from core import assign_shader



class PreviewWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(PreviewWidget, self).__init__(parent)

        ui_file = os.path.join(os.path.dirname(__file__), 'win.ui')
        _loadUi(ui_file, self)

        self.setWindowTitle('test Tool')
        self.switch_bool = self.get_radio_button_options(self.QFrame_opt) == 'from_version'
        self.init_layout()
        self.init_connectiond()
        test_path = 'X:/pipelinernd_rnd-0000/zzz_dev/test_shot/3d/anim/_publish/v005'
        self.lineEdit_path.setText(test_path)

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
        # print full_path
        # for abc in os.listdir(full_path):
        #     if os.path.splitext(abc)[-1] == '.abc':
        #         print os.path.splitext(abc)[0]
        abc_list = filter(lambda x: os.path.splitext(x)[-1] == '.abc', os.listdir(full_path))
        for abc in abc_list:
            abc_path = os.path.join(str(full_path), abc.encode())
            # TODO: anim pub should write out a json file, whcih like as follows:
            '''
            {"abc_name.abc": {"rigging_path": "",
                              "rigging_related_mod_path": ""}
            }
            '''
            metadata = {'asset_name': abc, 'abc_path': abc_path,
                        'namespace': abc.rsplit('.', 1)[0],
                        'shader_path': 'X:/pipelinernd_rnd-0000/zzz_dev/test_shot/3d/shd/_publish/v002/shaders_tex.ma',
                        'json_path': 'X:/pipelinernd_rnd-0000/zzz_dev/test_shot/3d/shd/_publish/v002/shader_tex.json'}
            self.listWidget_abc.add_item(basic_gui.MotionItem(abc, enable=True), metadata)

    def get_abc_from_version(self):
        version = self.get_combobox_options(self.comboBox_version)
        # full_path = os.path.join('/sw/...', version)
        # if os.path.exists(full_path):
        #     self.get_abc(full_path)
        print version

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