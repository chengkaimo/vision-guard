"""
    这个文件负责读帧
"""
import cv2
import config
# import os

def open_camera():
    cap = cv2.VideoCapture(config.SOURCE)
    # print(os.getcwd())
    # pass ❌ pass是留着占空位 填完要删 函数交结果要用return
    return cap

def read_frame(cap):
    ok, frame = cap.read()
    # pass
    return ok,frame