# -*- coding: utf-8 -*-
# @Datetime : 2023/9/30 17:28
# @Author   : WANGKANG
# @Blog     : kang17.xyz
# @File     : translate.py
# @brief    : 测试翻译接口
# Copyright 2023 WANGKANG, All Rights Reserved.
'''
调用百度api翻译文章
'''
import hashlib
import random
import traceback

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from utils.WkProperties import WkProperties

KEY = '',
APPID = ''


def read_api():
    global KEY, APPID
    try:
        property = WkProperties()
        property.parse_data("./api.properties")
        KEY = property.get("KEY")
        APPID = property.get("APPID")
        if not KEY or not APPID:
            return False
        else:
            return True
    except:
        return False


# 翻译线程
class TranslateThread(QThread):
    # 信号，触发信号，更新窗体中的数据
    translate_signal = pyqtSignal(str, str, int, QThread)
    
    def __init__(self, text, param, index, *args, **kwargs):
        # 本来这里是传入父组件，通过调用父组件中的destory_thread摧毁线程，但是这种方法不够安全，于是被抛弃
        super().__init__(*args, **kwargs)
        self.text = text
        self.param = param
        self.index = index
        # self.parent = parent
    
    def run(self):
        try:
            # while True:
            msg = translate_en2zh(self.text)
            if msg == 'Invalid Access Limit':
                msg = '请求过于频繁，请稍后再试！'
            self.translate_signal.emit(msg, self.param, self.index, self)
        # 本来这里有一个请求频繁就会自动重新请求的机制，后面我发现了更好的方式，就取消了
        # if msg != 'Invalid Access Limit':
        # 	break
        # else:
        # 	time.sleep(random.randint(0, 5))
        # print(msg)
        except:
            self.translate_signal.emit("出现未知异常！", self.param, self.index, self)
            print(traceback.format_exc())
        
        # 线程结束后，需要动态的移除此线程发，以免占用太多的系统资源
        # self.parent.destroy_thread(self)


class TranslateManyThread(QThread):
    # 信号，触发信号，更新窗体中的数据
    prefanyi_progress_signal = pyqtSignal(int)
    finish_prefanyi_signal = pyqtSignal(dict, str, QThread)
    
    def __init__(self, data_list: list[str], *args, **kwargs):
        # 本来这里是传入父组件，通过调用父组件中的destory_thread摧毁线程，但是这种方法不够安全，于是被抛弃
        super().__init__(*args, **kwargs)
        self.data_list = data_list
        self.total_len = len(data_list)
    
    def run(self):
        try:
            pre_fanyi_data = {}
            for idx, text in enumerate(self.data_list):
                msg = translate_en2zh(text)
                if msg == 'Invalid Access Limit':
                    msg = '请求过于频繁，请稍后再试！'
                self.prefanyi_progress_signal.emit(int(((idx + 1) / self.total_len) * 100))
                pre_fanyi_data.update({text: msg})
            self.finish_prefanyi_signal.emit(pre_fanyi_data, "预翻译成功！", self)
        except:
            self.finish_prefanyi_signal.emit(pre_fanyi_data, f"出现未知异常！\n{traceback.format_exc()}", self)
            print(traceback.format_exc())


def translate_en2zh(text):
    def md5(data):
        # appid + q + salt + 密钥
        str = data["appid"] + data["q"] + data["salt"] + KEY
        return hashlib.md5(str.encode("utf-8")).hexdigest()
    
    def random_num_10():
        return str(random.randint(10 ** 9, 10 ** 10 - 1))
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.43'
    }
    
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    
    data = {
        'q': text.strip().replace("\n", "@@"),
        'from': "en",
        'to': "zh",
        'appid': APPID,
        'salt': random_num_10(),
        'sign': "",
    }
    data["sign"] = md5(data)
    # print(data)
    json_data = requests.post(url=url, headers=headers, data=data).json()
    # print(json_data)
    if json_data.get('trans_result') is not None:
        res = json_data['trans_result'][0]['dst']
        res = res.replace("@@", "\n")
        return res
    else:
        return json_data['error_msg']


if __name__ == '__main__':
    # t = TranslateThread("apple")
    # t.start()
    # res = translate_en2zh("apple")
    # print(res)
    pass

# print(10 ** 5)
# print(10 ** 9, 10 ** 10 - 1)

# str = '2015063000000001apple143566028812345678'
# md5_obj = hashlib.md5(str.encode("utf-8"))
# print(md5_obj.hexdigest())

# f89f9594663708c1605f3d736d01d2d4
