"""
    这个文件负责交互数据库(保存报警相关信息)
"""
import threading
import time

import config
import sqlite3
import os


#流程：连接——做事情——提交——关闭

# 初始化数据库
def init_db():
    # 报警证据图目录： exist_ok=True 存在，不报错 不存在，建立
    os.makedirs(config.ALARM_DIR, exist_ok=True)
    # 连接数据库： 文件如果不存在，sqlite会自建
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    #建表
    cursor.execute("CREATE TABLE IF NOT EXISTS alarms (id INTEGER PRIMARY KEY AUTOINCREMENT, time TEXT, class_name TEXT, conf REAL, image_path TEXT)")
    #提交
    conn.commit()
    conn.close()


def save_alarm(class_name, conf, image_path):
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    # 时间字符串     strftime是格式化 time.time()是1970到现在的时间 算时间差
    t = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("INSERT INTO alarms (time, class_name, conf, image_path) VALUES (?,?,?,?)", (t, class_name, conf, image_path))
    conn.commit()
    conn.close()
