"""
    这个文件专门用来质检视频素材
"""

import cv2
import sys
from ultralytics import YOLO

# sys.argv = 命令行参数清单
#跑质检：.venv\Scripts\python.exe vg/qc_video.py data/raw/fire.mp4 weights/fire_smoke_yolov8n.pt
path = sys.argv[1]          # 命令行第一个参数：视频路径
model_path = sys.argv[2]    # 命令行第二个参数：权重路径
conf = 0.3
if len(sys.argv) > 3:       #如果命令行给了第三个参数，用给的 否则默认0.3
    conf = float(sys.argv[3])

model = YOLO(model_path)
cap = cv2.VideoCapture(path)

total = 0
hit = 0
while True:
    ok, frame = cap.read()
    if not ok:
        break
    total = total + 1
    if total % 30 != 0:     # 每30帧抽1帧 约每秒1帧
        continue
    results = model.predict(frame, conf=conf, verbose=False)
    names = results[0].names
    count = 0
    for box in results[0].boxes:
        cid = int(box.cls[0])
        print("  抽到：", names[cid], round(float(box.conf[0]), 2) )
        count = count + 1
    if count > 0:
        hit = hit + 1

cap.release()
print("抽样帧数：", total // 30,"有目标的帧：", hit)