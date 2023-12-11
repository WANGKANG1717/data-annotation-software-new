# -*- coding: utf-8 -*-
# @Date     : 2023-10-14 13:54:19
# @Author   : WangKang
# @Blog     : kang17.xyz
# @Email    : 1686617586@qq.com
# @Filepath : WkProperties.py
# @Brief    : 解析properties
# Copyright 2023 WANGKANG, All Rights Reserved.

import os
import traceback


class WkProperties:
    FILE_NOT_EXISTS = "文件不存在"
    INCORRECT_FORMAT = "格式有误"
    
    def __init__(self) -> None:
        self.key_value = {}
        self.content = None  # 文件内容
    
    def parse_data(self, filepath):
        """
        读取并解析数据
        :param filepath: 读取文件路径
        """
        if not filepath:
            return
        if not os.path.exists(filepath):
            raise Exception(self.FILE_NOT_EXISTS)
        with open(filepath, "r", encoding="utf-8") as f:
            self.content = f.read()
        self.key_value.clear()
        for line in self.content.split("\n"):
            line = line.strip().split("#")[0]  # 跳过注释
            if not line:
                continue
            if line.find("=") == -1:
                raise Exception(self.INCORRECT_FORMAT)
            data = line.split("=", 1)
            # print(data)
            key = data[0].strip()
            value = data[1].strip()
            self.key_value[key] = value
    
    def save_data(self, filepath):
        """
        保存数据，这里可以考虑添加保存文件时的方式：追加/覆盖
        :param filepath: 保存文件路径
        :return True: 保存成功  False: 保存失败
        """
        if not filepath:
            return True
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("# WkProperties created by WANGKANG\n")
                for key, data in self.key_value.items():
                    f.write(f"{key} = {data}\n")
            return True
        except:
            print("文件保存失败：", traceback.format_exc())
            return False
    
    def get(self, key):
        return self.key_value.get(key)
    
    def get_dict(self):
        return self.key_value
    
    def items(self):
        return self.key_value.items()
    
    def keys(self):
        return self.key_value.keys()
    
    def values(self):
        return self.key_value.values()
    
    def update(self, data: dict):
        self.key_value.update(data)
    
    def clear(self):
        self.key_value.clear()


if __name__ == "__main__":
    path = "./application.properties"
    property = WkProperties()
    property.parse_data(path)
    print(property.get("KEY"))
    print(property.get("APPID"))
    print(property.keys())
    print(property.values())
    
    property.save_data("./app.properties")
    
    print(property.get_dict())
    
    property.update({"key1": 123213, "saadsds": "1111", "ddddd": False})
    
    print(property.get_dict())
    property.save_data("./app1.properties")
