# -*- coding: utf-8 -*-
# @Datetime : 2023/12/8 12:21
# @Author   : WANGKANG
# @Blog     : 121.41.110.43
# @File     : MyWindow.py
# @brief    : 主程序封装
# Copyright 2023 WANGKANG, All Rights Reserved.
import json
import os.path
import traceback

import pandas as pd
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QFileDialog

from utils.dialog_text import *
from utils.mainwindow import Ui_mainWindow
from utils.translate import TranslateThread


class MainWindow(QMainWindow, Ui_mainWindow):
    ERROR_TRANSLATE = [
        '出现未知异常！',
        '请求过于频繁，请稍后再试！',
    ]
    FANYI_FILE_PATH = "./translate_map_content_fanyi.json"
    
    COMBOBOX_TAGS = ['fluency', 'clarity', 'concise', 'relevance',
                     'consistency', 'answerability', 'answer_consistency', 'acceptance'
                     ]
    COMBOBOX_MAX_INDEX = 3  # 最大下标
    
    # 初始化ui
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.setupUi(self)
        self.init_signal()
        #
        self.setWindowTitle('数据标注软件 By WANGKANG')
        self.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        self.setMinimumSize(800, 600)
        self.statusBar().showMessage('欢迎使用', 5000)  # 底部状态栏的提醒
        self.spinBox_current_index.setAlignment(Qt.AlignRight)
        #
        self.file_path = ''  # 文件路径
        self.excel_data = pd.DataFrame()  # 总的excel信息
        self.data_size = 0  # 数据集大小
        self.current_index = 0  # 当前文章/问题下标
        # 本来这里是文章、问题、预测分别存放在一个字典中，后面发现其实可以统一到一个词典中，其结构为{“content”:“翻译”}
        self.translate_map_content_fanyi = {}  # 用来记录已经翻译的数据
        # 自动翻译
        self.passage_auto_translate = False
        self.answer_auto_translate = False
        self.prediction_auto_translate = False
        #
        self.translate_threads = []  # 翻译线程队列
        #
        self.already_save_file = True  # 方便退出脚本
        #
        self.disable_or_enable_components(True)  # 一开始需要禁用按钮 等到打开文件后再开启按钮
        
        try:
            self.read_fanyi_data()
        except Exception as e:
            dialog = QMessageBox(QMessageBox.Critical, '错误',
                                 f"读取翻译数据失败！\n{traceback.format_exc()}",
                                 QMessageBox.Yes)
            dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
            dialog.setIconPixmap(QPixmap())
            dialog.button(QMessageBox.Yes).setText("确定")
            dialog.exec_()
    
    def init_params(self):
        self.current_index = 0
        self.data_size = len(self.excel_data['id'])
        # self.translate_map_content_fanyi = {}  # 用来记录已经翻译的文章，避免每次都要翻译，浪费算力
        self.translate_threads = []  # 翻译线程队列
    
    #
    def disable_or_enable_components(self, flag):
        self.pushButton_next.setDisabled(flag)
        self.pushButton_pre.setDisabled(flag)
        #
        self.pushButton_passage_source.setDisabled(flag)
        self.pushButton_prediction_source.setDisabled(flag)
        self.pushButton_answer_source.setDisabled(flag)
        #
        self.pushButton_passage_translate.setDisabled(flag)
        self.pushButton_prediction_translate.setDisabled(flag)
        self.pushButton_answer_translate.setDisabled(flag)
        #
        self.checkBox_passage_auto_translate.setDisabled(flag)
        self.checkBox_prediction_auto_translate.setDisabled(flag)
        self.checkBox_answer_auto_translate.setDisabled(flag)
        #
        self.groupBox.setDisabled(flag)
        
        # 搜索功能
        self.lineEdit_search.setDisabled(flag)
        self.pushButton_search.setDisabled(flag)
        #
        self.spinBox_current_index.setDisabled(flag)
    
    #
    # # 信号与槽的设置
    def init_signal(self):
        self.action_open.triggered.connect(self.open_file)
        self.pushButton_next.clicked.connect(self.next_passage_prediction)
        self.pushButton_pre.clicked.connect(self.pre_passage_prediction)
        self.action_save.triggered.connect(self.save_file)
        #
        self.pushButton_passage_translate.clicked.connect(lambda: self.translate("passage"))
        self.pushButton_prediction_translate.clicked.connect(lambda: self.translate("prediction"))
        self.pushButton_answer_translate.clicked.connect(lambda: self.translate("answer"))
        #
        self.pushButton_passage_source.clicked.connect(lambda: self.to_source("passage"))
        self.pushButton_prediction_source.clicked.connect(lambda: self.to_source("prediction"))
        self.pushButton_answer_source.clicked.connect(lambda: self.to_source("answer"))
        #
        self.checkBox_passage_auto_translate.clicked.connect(lambda: self.auto_translate("passage"))
        self.checkBox_prediction_auto_translate.clicked.connect(lambda: self.auto_translate("prediction"))
        self.checkBox_answer_auto_translate.clicked.connect(lambda: self.auto_translate("answer"))
        #
        self.action_saveAs.triggered.connect(self.saveAs_file)
        self.action_exit.triggered.connect(self.close)
        #
        self.action_about.triggered.connect(self.show_about_dialog)
        self.action_help.triggered.connect(self.show_help_dialog)
        #
        self.pushButton_search.clicked.connect(self.search)
        #
        self.spinBox_current_index.editingFinished.connect(self.jump_to_target_page)
        # 设置comboBox信号
        self.comboBox_fluency.currentTextChanged.connect(lambda: self.change_comboBox("fluency"))
        self.comboBox_clarity.currentTextChanged.connect(lambda: self.change_comboBox("clarity"))
        self.comboBox_concise.currentTextChanged.connect(lambda: self.change_comboBox("concise"))
        self.comboBox_relevance.currentTextChanged.connect(lambda: self.change_comboBox("relevance"))
        self.comboBox_consistency.currentTextChanged.connect(lambda: self.change_comboBox("consistency"))
        self.comboBox_answerability.currentTextChanged.connect(lambda: self.change_comboBox("answerability"))
        self.comboBox_answer_consistency.currentTextChanged.connect(lambda: self.change_comboBox("answer_consistency"))
        self.comboBox_acceptance.currentTextChanged.connect(lambda: self.change_comboBox("acceptance"))
    
    def open_file(self):
        # print("open_file")
        try:
            path = QFileDialog.getOpenFileName(self, 'open')[0]
            if path:
                self.excel_data = pd.read_excel(path)
                self.file_path = path
                self.set_status_bar_msg("打开成功 " + path)
                self.init_component()
        except:
            print(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"文件打开失败，请检查文件内容是否正常！\n{traceback.format_exc()}")
            self.set_status_bar_msg("文件打开失败！")
    
    #
    def save_file(self):
        if not self.file_path:
            return
        try:
            self.excel_data.to_excel(self.file_path, index=False)
            self.set_status_bar_msg("文件保存成功")
            self.already_save_file = True
        except Exception as e:
            QMessageBox.critical(self, "错误", "文件保存失败，请检查是否有其他软件正在使用文件！")
            self.set_status_bar_msg("文件保存失败")
        
        try:
            self.save_fanyi_data()
        except Exception as e:
            dialog = QMessageBox(QMessageBox.Critical, '错误',
                                 f"保存翻译数据失败！可能是权限不足，请检查！\n{traceback.format_exc()}",
                                 QMessageBox.Yes)
            dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
            dialog.setIconPixmap(QPixmap())
            dialog.button(QMessageBox.Yes).setText("确定")
            dialog.exec_()
    
    def saveAs_file(self):
        if not self.file_path:
            return
        path = QFileDialog.getSaveFileName(self, '另存为', '/', 'xlsx(*.xlsx);')[0]
        if path:
            self.file_path = path
            self.save_file()
    
    def init_component(self):
        self.init_params()
        self.disable_or_enable_components(False)
        self.get_set_ui_from_source()
    
    #
    def set_status_bar_msg(self, msg, timeout=5000):
        self.statusBar().showMessage(msg, timeout)
    
    #
    def get_set_text_to_ui(self, key):
        config = vars(self)
        text = self.excel_data.loc[self.current_index, key]
        config[f"textBrowser_{key}"].setText(text)
    
    def get_document_id(self):
        return self.excel_data.loc[self.current_index, 'id'].strip()
    
    #
    def next_passage_prediction(self):
        if self.current_index < self.data_size - 1:
            self.current_index += 1
            self.get_set_ui_from_source()
        else:
            QMessageBox.warning(self, "警告", "已经是最后一个问题！")
    
    #
    def pre_passage_prediction(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.get_set_ui_from_source()
        else:
            QMessageBox.warning(self, "警告", "已经是第一个问题！")
    
    def get_column_text(self, column_name):
        obj = self.excel_data.loc[self.current_index, column_name]
        # print(type(obj))
        if pd.isna(obj):
            return ""
        else:
            return str(obj).strip()
    
    def get_data_from_excel(self, key, index=None):
        if not index:
            return self.excel_data.loc[self.current_index, key]
        else:
            return self.excel_data.loc[index, key]
    
    def get_set_ui_from_source(self):
        self.already_save_file = False
        self.get_set_text_to_ui("passage")
        self.get_set_text_to_ui("answer")
        self.get_set_text_to_ui("prediction")
        self.label_id.setText(self.get_data_from_excel("id"))
        self.label_source.setText(self.get_data_from_excel("source"))
        #
        self.read_set_comboBox()
        #
        self.pushButton_passage_translate.setDisabled(self.passage_auto_translate)
        self.pushButton_prediction_translate.setDisabled(self.prediction_auto_translate)
        self.pushButton_answer_translate.setDisabled(self.answer_auto_translate)
        #
        if self.passage_auto_translate:
            self.translate("passage")
        if self.prediction_auto_translate:
            self.translate("prediction")
        if self.answer_auto_translate:
            self.translate("answer")
        
        self.init_progress()
    
    def translate(self, param):
        # todo 不知到为什么，明明可以拿到数据，但是死活没法识别
        config = vars(self)
        config[f'pushButton_{param}_translate'].setDisabled(True)
        config[f'pushButton_{param}_source'].setDisabled(False)
        if self.translate_map_content_fanyi.get(self.get_data_from_excel(param)) is not None:
            config[f'textBrowser_{param}'].setText(
                self.translate_map_content_fanyi.get(self.get_data_from_excel(param)))
            return
        
        new_thread = TranslateThread(self.get_column_text(param), param, self.current_index, self)
        new_thread.translate_signal.connect(self.update_translate_to_ui)
        new_thread.start()
        
        self.translate_threads.append(new_thread)  # 向线程队列中添加线程
    
    #
    def destroy_thread(self, thread):
        self.translate_threads.remove(thread)
        # print(f"已经移除线程{thread}")
        # print(self.translate_threads)
    
    def update_translate_to_ui(self, translate_text, param, index):
        self.set_status_bar_msg("翻译完成")
        
        config = vars(self)
        config[f'pushButton_{param}_translate'].setDisabled(True)
        config[f'pushButton_{param}_source'].setDisabled(False)
        config[f'textBrowser_{param}'].setText(translate_text)
        if translate_text not in self.ERROR_TRANSLATE:
            self.translate_map_content_fanyi[self.get_data_from_excel(param, index)] = translate_text
    
    def to_source(self, param):
        if param == "passage":
            self.pushButton_passage_translate.setDisabled(False)
            self.pushButton_passage_source.setDisabled(True)
            self.textBrowser_passage.setText(self.get_column_text(param))
        elif param == "prediction":
            self.pushButton_prediction_translate.setDisabled(False)
            self.pushButton_prediction_source.setDisabled(True)
            self.textBrowser_prediction.setText(self.get_column_text(param))
        elif param == "answer":
            self.pushButton_answer_translate.setDisabled(False)
            self.pushButton_answer_source.setDisabled(True)
            self.textBrowser_answer.setText(self.get_column_text(param))
    
    def auto_translate(self, param):
        if param == "passage":
            self.passage_auto_translate = self.checkBox_passage_auto_translate.isChecked()
        elif param == "prediction":
            self.prediction_auto_translate = self.checkBox_prediction_auto_translate.isChecked()
        elif param == "answer":
            self.answer_auto_translate = self.checkBox_answer_auto_translate.isChecked()
        self.translate(param)
    
    #
    def closeEvent(self, e):
        if self.file_path == "" or self.already_save_file:
            return
        dialog = QMessageBox(QMessageBox.Question, '提示', '关闭之前是否保存文件',
                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        # dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Save).setText("保存")
        dialog.button(QMessageBox.Discard).setText("放弃")
        dialog.button(QMessageBox.Cancel).setText("取消")
        answer = dialog.exec_()
        if answer == QMessageBox.Save:
            self.save_file()
        elif answer == QMessageBox.Cancel:
            e.ignore()  # 如果点击X号，或者点击cancel则只需要终止关闭窗口的事件
    
    def show_about_dialog(self):
        # with open("./dialog/about.html") as f:
        # 	about_text = f.read()
        text = DIALOG_ABOUT_HTML
        dialog = QMessageBox(QMessageBox.Information, "关于", text, QMessageBox.Yes)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Yes).setText("确定")
        dialog.exec_()
    
    #
    def show_help_dialog(self):
        # with open("./dialog/help.html") as f:
        # 	about_text = f.read()
        text = DIALOG_HELP_HTML
        dialog = QMessageBox(QMessageBox.Information, "帮助", text, QMessageBox.Yes)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Yes).setText("确定")
        dialog.exec_()
    
    def init_progress(self):
        # text = f"{self.current_index + 1} / {self.data_size}"
        text = f"/ {self.data_size}"
        self.label_total_length.setText(text)
        self.spinBox_current_index.setRange(1, self.data_size)
        self.spinBox_current_index.setValue(self.current_index + 1)
    
    #
    def search(self):
        key = self.lineEdit_search.text().strip()
        if key is None or key == "":
            return
        passage = self.textBrowser_passage.toPlainText()
        passage_new = passage.replace(key, f"<b>{key}</b>").replace('\n', "<br>")
        self.textBrowser_passage.setText(passage_new)
    
    def jump_to_target_page(self):
        # print(self.spinBox_current_index.value())
        self.current_index = self.spinBox_current_index.value() - 1
        self.get_set_ui_from_source()
    
    def save_fanyi_data(self):
        print("save_fanyi_data")
        with open(self.FANYI_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(self.translate_map_content_fanyi, f)
        # print(self.translate_map_content_fanyi)
    
    def read_fanyi_data(self):
        print("read_fanyi_data")
        if os.path.exists("./translate_map_content_fanyi.json"):
            with open(self.FANYI_FILE_PATH, "r", encoding="utf-8") as f:
                self.translate_map_content_fanyi = json.load(f)
        # print(self.translate_map_content_fanyi)
    
    def read_set_comboBox(self):
        print('read_set_comboBox')
        try:
            config = vars(self)
            for tag in self.COMBOBOX_TAGS:
                index = 0
                if self.get_column_text(tag):
                    index = int(self.get_data_from_excel(tag))
                    if index < 0 or index > self.COMBOBOX_MAX_INDEX:
                        index = 0
                config[f'comboBox_{tag}'].setCurrentIndex(index)
        except:
            print(traceback.format_exc())
    
    def change_comboBox(self, tag):
        try:
            config = vars(self)
            print(tag, config[f'comboBox_{tag}'].currentIndex())
            self.excel_data.loc[self.current_index, tag] = config[f'comboBox_{tag}'].currentIndex()
            # print(self.excel_data.loc[self.current_index, :])
        except:
            print(traceback.format_exc())
