# -*- coding: utf-8 -*-
# @Datetime : 2023-12-08 15:59:37
# @Author   : WANGKANG
# @Email    : 1686617586@qq.com
# @Blog     : 121.41.110.43
# @File     : main.py
# @brief    : 数据标注软件
# Copyright 2023 WANGKANG, All Rights Reserved.

import sys
from PyQt5.QtWidgets import QApplication
from utils.MyWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
