# -*- coding: utf-8 -*-
# @Datetime : 2023/10/2 12:21
# @Author   : WANGKANG
# @Blog     : kang17.xyz
# @File     : MyWindow.py
# @brief    : 主程序封装
# Copyright 2023 WANGKANG, All Rights Reserved.

import traceback

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QMainWindow

from utils.mainwindow import Ui_mainWindow

import pandas as pd
from utils.translate import TranslateThread
from utils.dialog_text import *


class MainWindow(QMainWindow, Ui_mainWindow):
    
    ERROR_TRANSLATE = [
        '出现未知异常！',
        '请求过于频繁，请稍后再试！',
    ]
    
    # 初始化ui
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        
        self.setupUi(self)
        self.init_signal()
        #
        # self.setWindowTitle('数据标注软件 By WANGKANG')
        # self.setMinimumSize(800, 600)
        # self.statusBar().showMessage('欢迎使用', 5000)  # 底部状态栏的提醒
        #
        # self.file_path = ''  # 文件路径
        # self.excel_data = pd.DataFrame()  # 总的excel信息
        # self.passage = ""  # 当前文章
        # self.prediction = ""  # 当前问题
        # self.target = ""
        # self.data_size = -1  # 数据集大小
        # self.current_index = 0  # 当前文章/问题下标
        # self.answerable = True  # 问题是否可回答
        # self.consistent = True  # 问题一致性 如果答案不可回答，则一致性为False
        # self.translate_map_passage = {}  # 用来记录已经翻译的文章，避免每次都要翻译，浪费算力
        # self.translate_map_prediction = {}
        # self.translate_map_target = {}
        # self.translate_map_answer = {}
        # self.translate_threads = []  # 翻译线程队列
        # self.passage_auto_translate = False  # 自动翻译
        # self.prediction_auto_translate = False
        # self.target_auto_translate = False
        # self.answer_auto_translate = False
        #
        # self.already_save_file = True  # 方便退出脚本
        #
        # self.disable_components()  # 一开始需要禁用按钮 等到打开文件后再开启按钮
    #
    # def init_params(self):
    #     self.current_index = 0
    #     self.data_size = len(self.excel_data['passage'])
    #     self.translate_map_passage = {}  # 用来记录已经翻译的文章，避免每次都要翻译，浪费算力
    #     self.translate_map_prediction = {}
    #     self.translate_map_target = {}
    #     self.translate_map_answer = {}
    #     self.translate_threads = []  # 翻译线程队列
    #
    # def disable_components(self):
    #     self.pushButton_next.setDisabled(True)
    #     self.pushButton_pre.setDisabled(True)
    #     self.radioButton_answerable.setDisabled(True)
    #     self.radioButton_unanswerable.setDisabled(True)
    #     self.comboBox_unanswerable_reason.setDisabled(True)
    #     self.lineEdit_unanswerable_notes.setDisabled(True)
    #     self.radioButton_consistent.setDisabled(True)
    #     self.radioButton_unconsistent.setDisabled(True)
    #     self.pushButton_notes_confirm.setDisabled(True)
    #     #
    #     self.pushButton_article_source.setDisabled(True)
    #     self.pushButton_prediction_source.setDisabled(True)
    #     self.pushButton_target_source.setDisabled(True)
    #     self.pushButton_answer_source.setDisabled(True)
    #     #
    #     self.pushButton_article_translate.setDisabled(True)
    #     self.pushButton_prediction_translate.setDisabled(True)
    #     self.pushButton_target_translate.setDisabled(True)
    #     self.pushButton_answer_translate.setDisabled(True)
    #     #
    #     self.checkBox_article_auto_translate.setDisabled(True)
    #     self.checkBox_prediction_auto_translate.setDisabled(True)
    #     self.checkBox_target_auto_translate.setDisabled(True)
    #     self.checkBox_answer_auto_translate.setDisabled(True)
    #     # 搜索功能
    #     self.lineEdit_search.setDisabled(True)
    #     self.pushButton_search.setDisabled(True)
    #
    # def enable_components(self):
    #     self.pushButton_next.setDisabled(False)
    #     self.pushButton_pre.setDisabled(False)
    #     self.radioButton_answerable.setDisabled(False)
    #     self.radioButton_unanswerable.setDisabled(False)
    #     self.comboBox_unanswerable_reason.setDisabled(False)
    #     # self.lineEdit_unanswerable_notes.setDisabled(False)
    #     self.radioButton_consistent.setDisabled(False)
    #     self.radioButton_unconsistent.setDisabled(False)
    #     # self.pushButton_notes_confirm.setDisabled(False)
    #     #
    #     self.pushButton_article_source.setDisabled(False)
    #     self.pushButton_prediction_source.setDisabled(False)
    #     self.pushButton_target_source.setDisabled(False)
    #     self.pushButton_answer_source.setDisabled(False)
    #     #
    #     self.pushButton_article_translate.setDisabled(False)
    #     self.pushButton_prediction_translate.setDisabled(False)
    #     self.pushButton_target_translate.setDisabled(False)
    #     self.pushButton_answer_translate.setDisabled(False)
    #     #
    #     self.checkBox_article_auto_translate.setDisabled(False)
    #     self.checkBox_prediction_auto_translate.setDisabled(False)
    #     self.checkBox_target_auto_translate.setDisabled(False)
    #     self.checkBox_answer_auto_translate.setDisabled(False)
    #     #
    #     # 搜索功能
    #     self.lineEdit_search.setDisabled(False)
    #     self.pushButton_search.setDisabled(False)
    #
    # # 信号与槽的设置
    def init_signal(self):
    #     self.action_open.triggered.connect(self.open_file)
    #     self.pushButton_next.clicked.connect(self.next_passage_prediction)
    #     self.pushButton_pre.clicked.connect(self.pre_passage_prediction)
    #     self.radioButton_answerable.clicked.connect(lambda: self.set_answerable(True))
    #     self.radioButton_unanswerable.clicked.connect(lambda: self.set_answerable(False))
    #     self.radioButton_consistent.clicked.connect(lambda: self.set_consistent(True))
    #     self.radioButton_unconsistent.clicked.connect(lambda: self.set_consistent(False))
    #     self.comboBox_unanswerable_reason.currentIndexChanged.connect(self.change_unanswerable_reason)
    #     self.pushButton_notes_confirm.clicked.connect(self.set_notes)
    #     self.action_save.triggered.connect(self.save_file)
    #     #
    #     self.pushButton_article_translate.clicked.connect(lambda: self.translate("passage"))
    #     self.pushButton_prediction_translate.clicked.connect(lambda: self.translate("prediction"))
    #     self.pushButton_target_translate.clicked.connect(lambda: self.translate("target"))
    #     self.pushButton_answer_translate.clicked.connect(lambda: self.translate("answer"))
    #     #
    #     self.pushButton_article_source.clicked.connect(lambda: self.to_source("passage"))
    #     self.pushButton_prediction_source.clicked.connect(lambda: self.to_source("prediction"))
    #     self.pushButton_target_source.clicked.connect(lambda: self.to_source("target"))
    #     self.pushButton_answer_source.clicked.connect(lambda: self.to_source("answer"))
    #     #
    #     self.checkBox_article_auto_translate.clicked.connect(lambda: self.auto_translate("passage"))
    #     self.checkBox_prediction_auto_translate.clicked.connect(lambda: self.auto_translate("prediction"))
    #     self.checkBox_target_auto_translate.clicked.connect(lambda: self.auto_translate("target"))
    #     self.checkBox_answer_auto_translate.clicked.connect(lambda: self.auto_translate("answer"))
    #     #
    #     self.action_saveAs.triggered.connect(self.saveAs_file)
    #     self.action_exit.triggered.connect(self.close)
        #
        self.action_about.triggered.connect(self.show_about_dialog)
        self.action_help.triggered.connect(self.show_help_dialog)
    #     #
    #     self.pushButton_search.clicked.connect(self.search)
    #
    # def open_file(self):
    #     # print("open_file")
    #     try:
    #         path = QFileDialog.getOpenFileName(self, 'open')[0]
    #         if path:
    #             self.excel_data = pd.read_excel(path)
    #             self.file_path = path
    #             self.set_status_bar_msg("打开成功 " + path)
    #             self.init_component()
    #     except:
    #         print(traceback.format_exc())
    #         QMessageBox.critical(self, "错误", "文件打开失败，请检查文件内容是否正常！")
    #         self.set_status_bar_msg("文件打开失败！")
    #
    # def save_file(self):
    #     if not self.file_path:
    #         return
    #     try:
    #         self.excel_data.to_excel(self.file_path, index=False)
    #         self.set_status_bar_msg("文件保存成功")
    #         self.already_save_file = True
    #     except Exception as e:
    #         QMessageBox.critical(self, "错误", "文件保存失败，请检查是否有其他软件正在使用文件！")
    #         self.set_status_bar_msg("文件保存失败")
    #
    # def saveAs_file(self):
    #     if not self.file_path:
    #         return
    #     path = QFileDialog.getSaveFileName(self, '另存为')[0]
    #     if path:
    #         self.file_path = path
    #         self.save_file()
    #
    # def init_component(self):
    #     self.init_params()
    #     self.enable_components()
    #     self.get_set_ui_from_source()
    #
    # def set_status_bar_msg(self, msg, timeout=5000):
    #     self.statusBar().showMessage(msg, timeout)
    #
    # def getPassage(self):
    #     self.passage = self.excel_data.loc[self.current_index, 'passage']
    #     # print(self.passage)
    #     self.textBrowser_passage.setText(self.passage)
    #
    # def getprediction(self):
    #     self.prediction = self.excel_data.loc[self.current_index, 'prediction']
    #     # print(self.prediction)
    #     self.textBrowser_prediction.setText(self.prediction)
    #
    # def getTarget(self):
    #     self.target = self.excel_data.loc[self.current_index, 'target']
    #     # print(self.prediction)
    #     self.textBrowser_target.setText(self.target)
    #
    # def get_document_id(self):
    #     return self.excel_data.iloc[self.current_index, 0].strip()
    #
    # def next_passage_prediction(self):
    #     # 这里首先要确保不可回答-其他 备注要填上
    #     if self.answerable == False:
    #         if self.comboBox_unanswerable_reason.currentIndex() == 0:
    #             QMessageBox.warning(self, "警告", "请选择原因！")
    #             return
    #         if self.comboBox_unanswerable_reason.currentIndex() == 6 and not self.set_notes():
    #             return
    #     if self.current_index < self.data_size - 1:
    #         self.current_index += 1
    #         # 这里为了软件的通用性，需要先获取表格中原来的信息，如果表格中原来不存在值，就重新赋一个新的值
    #         self.get_set_ui_from_source()
    #     else:
    #         QMessageBox.warning(self, "警告", "已经是最后一个问题！")
    #
    # def pre_passage_prediction(self):
    #     if self.current_index > 0:
    #         self.current_index -= 1
    #         self.get_set_ui_from_source()
    #     else:
    #         QMessageBox.warning(self, "警告", "已经是第一个问题！")
    #
    # def init_radio_button(self):
    #     self.init_radio_answerable()
    #     self.init_radio_consistent()
    #
    # #  用来改变按钮的状态，同时改变excel种的值
    # def change_answerable(self):
    #     if self.answerable:
    #         self.excel_data.loc[self.current_index, 'label'] = "answerable"
    #     else:
    #         self.excel_data.loc[self.current_index, 'answer_consistency'] = '0'
    #     self.init_radio_button()
    #
    # def change_consistent(self):
    #     self.excel_data.loc[self.current_index, 'answer_consistency'] = '1' if self.consistent else '0'
    #     self.init_radio_button()
    #
    # def set_consistent(self, flag):
    #     self.consistent = flag
    #     self.change_consistent()
    #
    # def set_answerable(self, flag):
    #     self.answerable = flag
    #     if not self.answerable:  # 保证一致性
    #         self.consistent = False
    #     else:
    #         self.comboBox_unanswerable_reason.setCurrentIndex(0)
    #     self.change_answerable()
    #
    # def change_unanswerable_reason(self):
    #     index = self.comboBox_unanswerable_reason.currentIndex()
    #     # print(index)
    #     self.excel_data.loc[self.current_index, 'label'] = "unanswerable:" + self.UNANSWERABLE_REASON_MAP[index]
    #
    #     # 只有当index == 6 时才会放开
    #     if index == 6:
    #         self.lineEdit_unanswerable_notes.setDisabled(False)
    #         self.pushButton_notes_confirm.setDisabled(False)
    #     else:
    #         self.lineEdit_unanswerable_notes.setDisabled(True)
    #         self.pushButton_notes_confirm.setDisabled(True)
    #
    # def set_notes(self):  # flag =True 说明是other错误
    #     text = self.lineEdit_unanswerable_notes.text().strip()
    #     # print(text)
    #     if text == "":
    #         QMessageBox.warning(self, "警告", "备注为空")
    #         return False
    #     self.excel_data.loc[self.current_index, "备注"] = text
    #     # print(self.excel_data.loc[self.current_index, ['label', 'answer_consistency', "备注"]])
    #     return True
    #
    # def get_column_text(self, column_name):
    #     obj = self.excel_data.loc[self.current_index, column_name]
    #     # print(type(obj))
    #     if pd.isna(obj):
    #         return ""
    #     else:
    #         if column_name == 'answer_consistency':
    #             return str(int(obj))
    #         else:
    #             return str(obj).strip()
    #
    # def judge_answerable(self):
    #     text = self.get_column_text("label")
    #     if text == "" or text == 'answerable':
    #         return True
    #     else:
    #         return False
    #
    # def judge_consistent(self):
    #     text = self.get_column_text("answer_consistency")
    #     if text == "" or text == '1':
    #         return True
    #     else:
    #         return False
    #
    # def get_set_ui_from_source(self):
    #     self.already_save_file = False
    #     self.getPassage()
    #     self.getprediction()
    #     self.getTarget()
    #     self.getAnswer()
    #
    #     self.set_answerable(self.judge_answerable())
    #     self.set_consistent(self.judge_consistent())
    #     # self.init_radio_button()
    #     #
    #     if not self.answerable:
    #         try:
    #             reason = self.get_column_text("label").split(":")[1]
    #             index = self.UNANSWERABLE_REASON_MAP2[reason]
    #         except:
    #             index = 0
    #         self.comboBox_unanswerable_reason.setCurrentIndex(index)
    #     #
    #     self.lineEdit_unanswerable_notes.setText(self.get_column_text("备注"))
    #     #
    #     self.pushButton_article_translate.setDisabled(self.passage_auto_translate)
    #     self.pushButton_prediction_translate.setDisabled(self.prediction_auto_translate)
    #     self.pushButton_target_translate.setDisabled(self.target_auto_translate)
    #     self.pushButton_answer_translate.setDisabled(self.answer_auto_translate)
    #     #
    #     if self.passage_auto_translate:
    #         self.translate("passage")
    #     if self.prediction_auto_translate:
    #         self.translate("prediction")
    #     if self.target_auto_translate:
    #         self.translate("target")
    #     if self.answer_auto_translate:
    #         self.translate("answer")
    #
    #     self.init_progress()
    #
    # def init_radio_answerable(self):
    #     # 初始化组件状态
    #     if self.answerable:
    #         self.radioButton_answerable.setChecked(True)
    #
    #         self.radioButton_consistent.setDisabled(False)
    #         self.radioButton_unconsistent.setDisabled(False)
    #
    #         self.comboBox_unanswerable_reason.setDisabled(True)
    #         self.lineEdit_unanswerable_notes.setDisabled(True)
    #     else:
    #         self.radioButton_unanswerable.setChecked(True)
    #         self.radioButton_unconsistent.setChecked(True)
    #
    #         self.radioButton_consistent.setDisabled(True)
    #         self.radioButton_unconsistent.setDisabled(True)
    #
    #         self.comboBox_unanswerable_reason.setDisabled(False)
    #
    # # self.lineEdit_unanswerable_notes.setDisabled(False)
    #
    # def init_radio_consistent(self):
    #     if self.consistent:
    #         self.radioButton_consistent.setChecked(True)
    #     else:
    #         self.radioButton_unconsistent.setChecked(True)
    #
    # def getAnswer(self):
    #     self.textBrowser_answer.setText(self.get_column_text("answer"))
    #
    # def translate(self, param):
    #     if param == "passage":
    #         self.pushButton_article_translate.setDisabled(True)
    #         self.pushButton_article_source.setDisabled(False)
    #         if self.translate_map_passage.get(self.get_document_id()) is not None:
    #             self.textBrowser_passage.setText(self.translate_map_passage.get(self.get_document_id()))
    #             return
    #     elif param == "prediction":
    #         self.pushButton_prediction_translate.setDisabled(True)
    #         self.pushButton_prediction_source.setDisabled(False)
    #         if self.translate_map_prediction.get(self.current_index) is not None:
    #             self.textBrowser_prediction.setText(self.translate_map_prediction.get(self.current_index))
    #             return
    #     elif param == "target":
    #         self.pushButton_target_translate.setDisabled(True)
    #         self.pushButton_target_source.setDisabled(False)
    #         if self.translate_map_target.get(self.current_index) is not None:
    #             self.textBrowser_target.setText(self.translate_map_target.get(self.current_index))
    #             return
    #     elif param == "answer":
    #         self.pushButton_answer_translate.setDisabled(True)
    #         self.pushButton_answer_source.setDisabled(False)
    #         if self.translate_map_answer.get(self.current_index) is not None:
    #             self.textBrowser_answer.setText(self.translate_map_answer.get(self.current_index))
    #             return
    #
    #     new_thread = TranslateThread(self.get_column_text(param), param, self.current_index, self)
    #     new_thread.translate_signal.connect(self.update_translate_article)
    #     new_thread.start()
    #
    #     self.translate_threads.append(new_thread)  # 向线程队列中添加线程
    #
    # def destroy_thread(self, thread):
    #     self.translate_threads.remove(thread)
    #
    # # print(f"已经移除线程{thread}")
    # # print(self.translate_threads)
    #
    # def update_translate_article(self, translate_text, param, index):
    #     self.set_status_bar_msg("翻译完成")
    #     if param == "passage":
    #         self.pushButton_article_translate.setDisabled(True)
    #         self.pushButton_article_source.setDisabled(False)
    #         self.textBrowser_passage.setText(translate_text)
    #         if translate_text not in self.ERROR_TRANSLATE:
    #             self.translate_map_passage[self.get_document_id()] = translate_text
    #     elif param == "prediction":
    #         self.pushButton_prediction_translate.setDisabled(True)
    #         self.pushButton_prediction_source.setDisabled(False)
    #         self.textBrowser_prediction.setText(translate_text)
    #         if translate_text not in self.ERROR_TRANSLATE:
    #             self.translate_map_prediction[index] = translate_text
    #     elif param == "target":
    #         self.pushButton_target_translate.setDisabled(True)
    #         self.pushButton_target_source.setDisabled(False)
    #         self.textBrowser_target.setText(translate_text)
    #         if translate_text not in self.ERROR_TRANSLATE:
    #             self.translate_map_target[index] = translate_text
    #     elif param == "answer":
    #         self.pushButton_answer_translate.setDisabled(True)
    #         self.pushButton_answer_source.setDisabled(False)
    #         self.textBrowser_answer.setText(translate_text)
    #         if translate_text not in self.ERROR_TRANSLATE:
    #             self.translate_map_answer[index] = translate_text
    #
    # def to_source(self, param):
    #     if param == "passage":
    #         self.pushButton_article_translate.setDisabled(False)
    #         self.pushButton_article_source.setDisabled(True)
    #         self.textBrowser_passage.setText(self.get_column_text(param))
    #     elif param == "prediction":
    #         self.pushButton_prediction_translate.setDisabled(False)
    #         self.pushButton_prediction_source.setDisabled(True)
    #         self.textBrowser_prediction.setText(self.get_column_text(param))
    #     elif param == "target":
    #         self.pushButton_target_translate.setDisabled(False)
    #         self.pushButton_target_source.setDisabled(True)
    #         self.textBrowser_target.setText(self.get_column_text(param))
    #     elif param == "answer":
    #         self.pushButton_answer_translate.setDisabled(False)
    #         self.pushButton_answer_source.setDisabled(True)
    #         self.textBrowser_answer.setText(self.get_column_text(param))
    #
    # def auto_translate(self, param):
    #     if param == "passage":
    #         self.passage_auto_translate = self.checkBox_article_auto_translate.isChecked()
    #     elif param == "prediction":
    #         self.prediction_auto_translate = self.checkBox_prediction_auto_translate.isChecked()
    #     elif param == 'target':
    #         self.target_auto_translate = self.checkBox_target_auto_translate.isChecked()
    #     elif param == "answer":
    #         self.answer_auto_translate = self.checkBox_answer_auto_translate.isChecked()
    #     self.translate(param)
    #
    # def closeEvent(self, e):
    #     if self.file_path == "" or self.already_save_file:
    #         return
    #     answer = QMessageBox.question(self, '提示', '关闭之前是否保存文件',
    #                                   QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
    #     if answer == QMessageBox.Save:
    #         self.save_file()
    #     elif answer == QMessageBox.Cancel:
    #         e.ignore()  # 如果点击X号，或者点击cancel则只需要终止关闭窗口的事件
    #
    def show_about_dialog(self):
        # with open("./dialog/about.html") as f:
        # 	about_text = f.read()
        text = DIALOG_ABOUT_HTML
        QMessageBox.about(self, '关于', text)
    #
    def show_help_dialog(self):
        # with open("./dialog/help.html") as f:
        # 	about_text = f.read()
        text = DIALOG_HELP_HTML
        QMessageBox.about(self, '帮助', text)
    #
    # # 检测键盘回车按键
    # def keyPressEvent(self, event):
    #     if not self.comboBox_unanswerable_reason.isEnabled():
    #         return
    #     # print("按下：" + str(event.key()))
    #     if (event.key() == Qt.Key_1):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(1)
    #     if (event.key() == Qt.Key_2):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(2)
    #     if (event.key() == Qt.Key_3):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(3)
    #     if (event.key() == Qt.Key_4):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(4)
    #     if (event.key() == Qt.Key_5):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(5)
    #     if (event.key() == Qt.Key_6):
    #         self.comboBox_unanswerable_reason.setCurrentIndex(6)
    #
    # def init_progress(self):
    #     text = f"{self.current_index + 1} / {self.data_size}"
    #     self.label_progress.setText(text)
    #
    # def search(self):
    #     key = self.lineEdit_search.text().strip()
    #     if key is None or key == "":
    #         return
    #     passage = self.textBrowser_passage.toPlainText()
    #     passage_new = passage.replace(key, f"<b>{key}</b>").replace('\n', "<br>")
    #     self.textBrowser_passage.setText(passage_new)
