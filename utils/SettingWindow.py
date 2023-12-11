# -*- coding: utf-8 -*-
# @Datetime : 2023/12/11 13:22
# @Author   : WANGKANG
# @Email    : 1686617586@qq.com
# @Blog     : 121.41.110.43
# @File     : SettingWindow.py
# @brief    : 设置窗口
# Copyright 2023 WANGKANG, All Rights Reserved.
import os
import sys

from PyQt5.QtWidgets import *

import utils.translate
from utils.setting_window import Ui_Form


class SettingWindow(QMainWindow, Ui_Form):
    # 初始化ui
    def __init__(self, parent):
        super(SettingWindow, self).__init__()
        
        self.setupUi(self)
        self.parent = parent
        self.init_ui()
        self.init_signal()
    
    # 信号与槽的设置
    def init_signal(self):
        self.pushButton_clear.clicked.connect(self.clear_api_data)
        self.pushButton_confirm_api.clicked.connect(self.confirm_api)
        self.pushButton_confirm_pos.clicked.connect(self.confirm_pos)
        self.pushButton_pos_reset.clicked.connect(self.pos_reset)
    
    def init_ui(self):
        print("init_ui")
        self.parent.read_api2()
        self.lineEdit_key.setText(utils.translate.KEY)
        self.lineEdit_appid.setText(utils.translate.APPID)
        # print(os.getcwd())
        self.parent.read_fanyi_file_path()
        self.lineEdit_translate_data_pos.setText(self.parent.FANYI_FILE_PATH)
    
    def clear_api_data(self):
        print('clear_api_data')
        self.lineEdit_key.setText("")
        self.lineEdit_appid.setText("")
    
    def confirm_api(self):
        print('confirm_api')
        key = self.lineEdit_key.text().strip()
        appid = self.lineEdit_appid.text().strip()
        self.parent.save_api2(key, appid)
    
    def confirm_pos(self):
        print('confirm_pos')
        pos = self.lineEdit_translate_data_pos.text()
        print(pos)
        self.parent.save_fanyi_file_path(pos)
    
    def pos_reset(self):
        print('pos_reset')
        self.parent.reset_fanyi_file_path()
        self.lineEdit_translate_data_pos.setText(self.parent.FANYI_FILE_PATH)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SettingWindow()
    window.show()
    sys.exit(app.exec_())
