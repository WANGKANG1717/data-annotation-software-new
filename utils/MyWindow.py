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
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QMessageBox, QMainWindow, QFileDialog, QProgressBar, QLabel

from utils.dialog_text import *
from utils.mainwindow import Ui_mainWindow
from utils.translate import TranslateThread, read_api, TranslateManyThread


class MainWindow(QMainWindow, Ui_mainWindow):
    APP_NAME = '数据标注软件 By WANGKANG'
    ERROR_TRANSLATE = [
        '出现未知异常！',
        '请求过于频繁，请稍后再试！',
    ]
    FANYI_FILE_PATH = "./translate_map_content_fanyi.json"
    
    COMBOBOX_TAGS = ['fluency', 'clarity', 'concise', 'relevance',
                     'consistency', 'answerability', 'answer_consistency', 'acceptance'
                     ]
    COMBOBOX_MAX_INDEX = 3  # 最大下标
    
    TAGS = ['passage', 'prediction', 'answer']
    
    # 初始化ui
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.init_signal()
        #
        self.progressLabel = None
        self.progressBar = None
        self.init_ui()
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
        self.translate_threads = []  # 翻译线程队列 # 翻译队列不需要经常重置
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
        if not read_api():
            dialog = QMessageBox(QMessageBox.Warning, '警告',
                                 f"读取翻译api失败，在线翻译功能将无法正常使用！",
                                 QMessageBox.Yes)
            dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
            dialog.button(QMessageBox.Yes).setText("确定")
            dialog.exec_()
    
    def init_ui(self):
        self.setWindowTitle(self.APP_NAME)
        self.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        self.setMinimumSize(800, 600)
        self.statusBar().showMessage('欢迎使用', 5000)  # 底部状态栏的提醒
        self.spinBox_current_index.setAlignment(Qt.AlignRight)
        self.progressBar = QProgressBar()
        self.progressLabel = QLabel("")
        self.progressBar.setMaximumWidth(200)
        self.progressBar.setMaximumHeight(17)
        # self.statusBar().addWidget(progressLabel) # 添加到状态栏的左边
        # self.statusBar().ddWidget(progressBar)
        self.statusBar().addPermanentWidget(self.progressLabel)  # 添加到状态栏的右边
        self.statusBar().addPermanentWidget(self.progressBar)
        self.progressBar.setVisible(False)
        self.progressLabel.setVisible(False)
    
    def init_params(self):
        self.current_index = 0
        self.data_size = len(self.excel_data['id'])
        # self.translate_map_content_fanyi = {}  # 用来记录已经翻译的文章，避免每次都要翻译，浪费算力
        # self.translate_threads = []  # 翻译线程队列
    
    #
    def disable_or_enable_components(self, flag):
        print('disable_or_enable_components')
        self.pushButton_next.setDisabled(flag)
        self.pushButton_pre.setDisabled(flag)
        #
        self.textBrowser_passage.setDisabled(flag)
        self.textBrowser_answer.setDisabled(flag)
        self.textBrowser_prediction.setDisabled(flag)
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
        self.spinBox_current_index.blockSignals(True)
        self.spinBox_current_index.setDisabled(flag)
        self.spinBox_current_index.blockSignals(False)
        # 关闭文件信号
        self.action_close.setDisabled(flag)
        self.action_save.setDisabled(flag)
        self.action_saveAs.setDisabled(flag)
        self.action_prefanyi.setDisabled(flag)
    
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
        #
        self.action_prefanyi.triggered.connect(self.prefanyi)
        #
        self.action_close.triggered.connect(self.close_file)
        #
        self.comboBox_fluency.currentTextChanged.connect(lambda: self.change_comboBox("fluency"))
        self.comboBox_clarity.currentTextChanged.connect(lambda: self.change_comboBox("clarity"))
        self.comboBox_concise.currentTextChanged.connect(lambda: self.change_comboBox("concise"))
        self.comboBox_relevance.currentTextChanged.connect(lambda: self.change_comboBox("relevance"))
        self.comboBox_consistency.currentTextChanged.connect(lambda: self.change_comboBox("consistency"))
        self.comboBox_answerability.currentTextChanged.connect(lambda: self.change_comboBox("answerability"))
        self.comboBox_answer_consistency.currentTextChanged.connect(
            lambda: self.change_comboBox("answer_consistency"))
        self.comboBox_acceptance.currentTextChanged.connect(lambda: self.change_comboBox("acceptance"))
    
    def block_signals(self, flag):
        # 有时候因为信号的原因，可能会导致一些异常的操作，所以在进行交大幅度的修改时，需要屏蔽信号
        # 结果发信时spinBox的信号触发问题，最后还是在函数里面手动阻塞信号才解决这个问题，有点无语
        print("block_signals")
        self.action_open.blockSignals(flag)
        self.pushButton_next.blockSignals(flag)
        self.pushButton_pre.blockSignals(flag)
        self.action_save.blockSignals(flag)
        #
        self.pushButton_passage_translate.blockSignals(flag)
        self.pushButton_prediction_translate.blockSignals(flag)
        self.pushButton_answer_translate.blockSignals(flag)
        #
        self.pushButton_passage_source.blockSignals(flag)
        self.pushButton_prediction_source.blockSignals(flag)
        self.pushButton_answer_source.blockSignals(flag)
        #
        self.checkBox_passage_auto_translate.blockSignals(flag)
        self.checkBox_prediction_auto_translate.blockSignals(flag)
        self.checkBox_answer_auto_translate.blockSignals(flag)
        #
        self.action_saveAs.blockSignals(flag)
        self.action_exit.blockSignals(flag)
        #
        self.action_about.blockSignals(flag)
        self.action_help.blockSignals(flag)
        #
        self.pushButton_search.blockSignals(flag)
        #
        self.spinBox_current_index.blockSignals(flag)
        #
        self.action_prefanyi.blockSignals(flag)
        #
        self.action_close.blockSignals(flag)
        #
        self.comboBox_fluency.blockSignals(flag)
        self.comboBox_clarity.blockSignals(flag)
        self.comboBox_concise.blockSignals(flag)
        self.comboBox_relevance.blockSignals(flag)
        self.comboBox_consistency.blockSignals(flag)
        self.comboBox_answerability.blockSignals(flag)
        self.comboBox_answer_consistency.blockSignals(flag)
        self.comboBox_acceptance.blockSignals(flag)
    
    def set_window_title(self):
        if not self.file_path:
            self.setWindowTitle(f"{'*' if not self.already_save_file else ''}{self.APP_NAME}")
        else:
            file_name = self.file_path.rsplit('/', 1)[1]
            self.setWindowTitle(f"{'*' if not self.already_save_file else ''}{self.APP_NAME} - {file_name}")
    
    def open_file(self):
        print("open_file")
        try:
            path = QFileDialog.getOpenFileName(self, 'open')[0]
            if path:
                self.excel_data = pd.read_excel(path)
                self.file_path = path
                self.set_status_bar_msg("打开成功 " + path)
                self.init_component()
                # print(self.file_path)
                self.set_window_title()
        except:
            print(traceback.format_exc())
            QMessageBox.critical(self, "错误", f"文件打开失败，请检查文件内容是否正常！\n{traceback.format_exc()}")
            self.set_status_bar_msg("文件打开失败！")
    
    def close_file(self):
        print("close_file")
        '''
        这里有一个奇怪的bug，如果点击下一页，然后直接ctrl+w关闭文件，会直接报错，不知到什么原因，不过被我用异常处理搞定了
        后面如果有时间还是得好好研究一下
        '''
        try:
            # self.block_signals(True)
            if not self.already_save_file:
                answer = self.save_or_not_dialog()
                if answer == QMessageBox.Save:
                    self.save_file()
                elif answer == QMessageBox.Cancel:
                    return
            self.file_path = ''  # 文件路径
            self.excel_data = pd.DataFrame()  # 总的excel信息
            self.data_size = 0  # 数据集大小
            self.current_index = 0  # 当前文章/问题下标
            self.already_save_file = True
            self.reset_textBrowser_or_other()
            self.reset_comboBox()
            self.reset_progress()
            self.set_window_title()
            self.disable_or_enable_components(True)
        except:
            print(traceback.format_exc())
        # self.block_signals(False)
    
    def save_file(self):
        if not self.file_path:
            return
        try:
            self.excel_data.to_excel(self.file_path, index=False)
            self.set_status_bar_msg("文件保存成功")
            self.already_save_file = True
            self.set_window_title()
        except Exception as e:
            QMessageBox.critical(self, "错误", "文件保存失败，请检查是否有其他软件正在使用文件！")
            self.set_status_bar_msg("文件保存失败")
        
        self.save_fanyi_data()
    
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
    
    def set_status_bar_msg(self, msg, timeout=5000):
        self.statusBar().showMessage(msg, timeout)
    
    def get_set_text_to_ui(self, key):
        config = vars(self)
        try:
            text = self.excel_data.loc[self.current_index, key]
        except:
            text = ""
            # print(traceback.format_exc())
        config[f"textBrowser_{key}"].setText(text)
    
    def get_document_id(self):
        return self.excel_data.loc[self.current_index, 'id'].strip()
    
    def next_passage_prediction(self):
        if self.current_index < self.data_size - 1:
            self.current_index += 1
            self.get_set_ui_from_source()
        else:
            QMessageBox.warning(self, "警告", "已经是最后一个问题！")
    
    def pre_passage_prediction(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.get_set_ui_from_source()
        else:
            QMessageBox.warning(self, "警告", "已经是第一个问题！")
    
    def get_column_text(self, column_name):
        try:
            obj = self.excel_data.loc[self.current_index, column_name]
            # print(type(obj))
            if pd.isna(obj):
                return ""
            else:
                return str(obj).strip()
        except:
            return ''
    
    def get_data_from_excel(self, key, index=None):
        try:
            if not index:
                return self.excel_data.loc[self.current_index, key]
            else:
                return self.excel_data.loc[index, key]
        except:
            return ""
    
    def get_set_ui_from_source(self):
        print("get_set_ui_from_source")
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
        print("translate")
        # todo 不知到为什么，明明可以拿到数据，但是死活没法识别
        config = vars(self)
        if not config[f'textBrowser_{param}'].isEnabled():
            return
        config[f'pushButton_{param}_translate'].setDisabled(True)
        config[f'pushButton_{param}_source'].setDisabled(False)
        if self.translate_map_content_fanyi.get(self.get_data_from_excel(param)) is not None:
            config[f'textBrowser_{param}'].setText(
                self.translate_map_content_fanyi.get(self.get_data_from_excel(param)))
            return
        
        new_thread = TranslateThread(self.get_column_text(param), param, self.current_index)
        new_thread.translate_signal.connect(self.update_translate_to_ui)
        self.translate_threads.append(new_thread)  # 向线程队列中添加线程
        new_thread.start()
    
    def remove_thread(self, thread):
        '''这里的摧毁线程没有用到，需要优化'''
        print(self.translate_threads)
        if thread in self.translate_threads:
            self.translate_threads.remove(thread)
            print(f"已经移除线程{thread}")
    
    def destroy_all_thread(self):
        # 暂时用不到
        for thread in self.translate_threads:
            thread.exit(0)
    
    def update_translate_to_ui(self, translate_text, param, index, thread):
        try:
            config = vars(self)
            self.set_status_bar_msg("翻译完成")
            self.remove_thread(thread)
            
            if not config[f'textBrowser_{param}'].isEnabled():
                return
            config[f'pushButton_{param}_translate'].setDisabled(True)
            config[f'pushButton_{param}_source'].setDisabled(False)
            if self.current_index == index:
                config[f'textBrowser_{param}'].setText(translate_text)
            if translate_text not in self.ERROR_TRANSLATE:
                self.translate_map_content_fanyi[self.get_data_from_excel(param, index)] = translate_text
        except:
            print(traceback.format_exc())
    
    def to_source(self, param):
        print("to_source")
        config = vars(self)
        if not config[f'textBrowser_{param}'].isEnabled():
            return
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
    
    def save_or_not_dialog(self):
        dialog = QMessageBox(QMessageBox.Question, '提示', '关闭之前是否保存文件',
                             QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        # dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Save).setText("保存")
        dialog.button(QMessageBox.Discard).setText("放弃")
        dialog.button(QMessageBox.Cancel).setText("取消")
        return dialog.exec_()
    
    def closeEvent(self, e):
        if self.file_path == "" or self.already_save_file:
            return
        answer = self.save_or_not_dialog()
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
        self.spinBox_current_index.blockSignals(True)
        self.spinBox_current_index.setRange(1, self.data_size)
        self.spinBox_current_index.setValue(self.current_index + 1)
        self.spinBox_current_index.blockSignals(False)
    
    def reset_progress(self):
        print("reset_progress")
        text = "/ 0"
        self.label_total_length.setText(text)
        self.spinBox_current_index.blockSignals(True)
        self.spinBox_current_index.setRange(0, self.data_size)
        self.spinBox_current_index.setValue(0)
        self.spinBox_current_index.blockSignals(False)
    
    def search(self):
        key = self.lineEdit_search.text().strip()
        if key is None or key == "":
            return
        passage = self.textBrowser_passage.toPlainText()
        passage_new = passage.replace(key, f"<b>{key}</b>").replace('\n', "<br>")
        self.textBrowser_passage.setText(passage_new)
    
    def jump_to_target_page(self):
        try:
            print("jump_to_target_page")
            # print(self.spinBox_current_index.value())
            self.current_index = self.spinBox_current_index.value() - 1
            self.get_set_ui_from_source()
        except:
            print(traceback.format_exc())
    
    def save_fanyi_data(self):
        print("save_fanyi_data")
        try:
            fanyi_data = {}
            if os.path.exists("./translate_map_content_fanyi.json"):
                with open(self.FANYI_FILE_PATH, "r", encoding="utf-8") as f:
                    fanyi_data = json.load(f)
            fanyi_data.update(self.translate_map_content_fanyi)
            with open(self.FANYI_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(fanyi_data, f)
            # print(self.translate_map_content_fanyi)
        except Exception as e:
            dialog = QMessageBox(QMessageBox.Critical, '错误',
                                 f"保存翻译数据失败！可能是权限不足，请检查！\n{traceback.format_exc()}",
                                 QMessageBox.Yes)
            dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
            dialog.setIconPixmap(QPixmap())
            dialog.button(QMessageBox.Yes).setText("确定")
            dialog.exec_()
    
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
                config[f'comboBox_{tag}'].blockSignals(True)
                config[f'comboBox_{tag}'].setCurrentIndex(index)
                config[f'comboBox_{tag}'].blockSignals(False)
        except:
            print(traceback.format_exc())
    
    def reset_comboBox(self):
        print('reset_comboBox')
        try:
            config = vars(self)
            for tag in self.COMBOBOX_TAGS:
                config[f'comboBox_{tag}'].blockSignals(True)
                config[f'comboBox_{tag}'].setCurrentIndex(0)
                config[f'comboBox_{tag}'].blockSignals(False)
        except:
            print(traceback.format_exc())
    
    def reset_textBrowser_or_other(self):
        print("reset_textBrowser_or_other")
        self.textBrowser_passage.setText("")
        self.textBrowser_answer.setText("")
        self.textBrowser_prediction.setText("")
        self.lineEdit_search.setText("")
        self.label_id.setText("")
        self.label_source.setText("")
    
    def change_comboBox(self, tag):
        print("change_comboBox")
        try:
            self.already_save_file = False
            self.set_window_title()
            config = vars(self)
            print(tag, config[f'comboBox_{tag}'].currentIndex())
            self.excel_data.loc[self.current_index, tag] = config[f'comboBox_{tag}'].currentIndex()
            # print(self.excel_data.loc[self.current_index, :])
        except:
            print(traceback.format_exc())
    
    # 预翻译所有文章，问题、答案，这样可以拿到结果后，供后面所有人使用
    def prefanyi(self):
        print("prefanyi")
        if not self.file_path:
            return
        # 用来存储需要翻译的所有数据
        all_data = []
        for index in range(self.data_size):
            for tag in self.TAGS:
                all_data.append(self.get_data_from_excel(tag, index))
        tmp_data = set(all_data)
        all_data = []
        for data in tmp_data:
            if self.translate_map_content_fanyi.get(data) is None:
                all_data.append(data)
        print("总共需要翻译的数据长度为：", len(all_data))
        char_length = len("".join(all_data))
        print(char_length)
        if len(all_data) == 0:
            dialog = QMessageBox(QMessageBox.Question, '提示', "所有翻译数据皆已缓存，无需翻译！", QMessageBox.Yes)
            dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
            # dialog.setIconPixmap(QPixmap())
            dialog.button(QMessageBox.Yes).setText("确定")
            dialog.exec_()
            return
        dialog = QMessageBox(QMessageBox.Question, '提示',
                             f'本次预翻译，共{len(all_data)}条数据，总字符为{char_length}。\n预翻译将会一次性翻译完打开文档中的所有英文文本，会消耗大量api翻译额度，可能会占用较长时间，是否继续？',
                             QMessageBox.Yes | QMessageBox.No)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        # dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Yes).setText("确定")
        dialog.button(QMessageBox.No).setText("取消")
        answer = dialog.exec_()
        if answer == QMessageBox.Yes:
            self.disable_or_enable_components(True)
            self.progressLabel.setText("请稍等...")
            self.progressBar.setRange(0, 100)
            self.progressBar.setValue(0)
            self.progressBar.setVisible(True)
            self.progressLabel.setVisible(True)
            self.prefanyi_main(all_data)
    
    def prefanyi_main(self, data_list):
        print("prefanyi_main")
        new_thread = TranslateManyThread(data_list)
        new_thread.prefanyi_progress_signal.connect(self.update_prefanyi_progress_to_ui)
        new_thread.finish_prefanyi_signal.connect(self.finish_prefanyi)
        self.translate_threads.append(new_thread)  # 向线程队列中添加线程
        new_thread.start()
    
    def update_prefanyi_progress_to_ui(self, progress: int):
        print("update_prefanyi_progress_to_ui")
        print(progress)
        self.progressBar.setValue(progress)
    
    def finish_prefanyi(self, prefanyi_data: dict, msg: str, thread):
        print("finish_prefanyi")
        print(prefanyi_data)
        self.translate_map_content_fanyi.update(prefanyi_data)
        # self.progressLabel.setText(msg)
        # 这里要过一会发信号让状态栏里面的组件消失
        self.hide_progressBar()
        self.remove_thread(thread)
        self.save_fanyi_data()
        self.disable_or_enable_components(False)
        
        if "成功" in msg:
            self.progressLabel.setText("预翻译完成")
            dialog = QMessageBox(QMessageBox.Information, '提示', msg, QMessageBox.Yes)
        else:
            self.progressLabel.setText("预翻译失败")
            dialog = QMessageBox(QMessageBox.Critical, '错误', msg, QMessageBox.Yes)
        dialog.setWindowIcon(QIcon(":/icons/logo_wk.ico"))
        # dialog.setIconPixmap(QPixmap())
        dialog.button(QMessageBox.Yes).setText("确定")
        dialog.exec_()
    
    def hide_progressBar(self):
        timer = QTimer(self)
        timer.start(5000)
        timer.timeout.connect(lambda: self.progressLabel.setVisible(False))
        timer.timeout.connect(lambda: self.progressBar.setVisible(False))
        timer.start()
