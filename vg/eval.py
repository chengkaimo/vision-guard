"""
    这是评测脚本 权重＋视频 生成一份报告
"""

import cv2
import time
import os
from ultralytics import YOLO
import settings

VIDEOS = [
    ("近景柴火", os.path.join(settings.BASE_DIR, "data", "raw", "fireclose1.ogv")),
    ("野火航拍", os.path.join(settings.BASE_DIR, "data", "raw", "wildfire1.webm")),
    ("弱火困难", os.path.join(settings.BASE_DIR, "data", "raw", "fire.mp4")),
    ("人群对照", os.path.join(settings.BASE_DIR, "data", "raw", "crowd1.mp4")),
]

WEIGHTS = [
    ("火焰烟雾v8n", os.path.join(settings.BASE_DIR, "weights", "fire_smoke_yolov8n.pt")),
    ("通用yolo11m", os.path.join(settings.BASE_DIR, "weights", "yolo11m.pt")),
]

CONF = 0.3 # 置信度阈值
STEP = 10  # 抽帧间隔


def eval_one(model, path):
    cap = cv2.VideoCapture(path)
    total = 0
    hit = 0
    boxes= 0
    conf_sum = 0.0
    ms_sum = 0.0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        total = total + 1
        if total % STEP !=0:
            continue
        t0 = time.time()
        results = model.predict(frame, conf=CONF, verbose=False)
        ms_sum = ms_sum + (time.time() - t0) * 1000
        n = len(results[0].boxes)
        boxes = boxes + n
        if n > 0:
            hit = hit + 1
        for b in results[0].boxes:
            conf_sum = conf_sum + float(b.conf[0])
    cap.release()

    samples = total // STEP     # 抽了几帧
    rate = 0.0
    if samples > 0:
        rate = hit / samples    # 命中率
    avg_conf = 0.0
    if boxes > 0:
        avg_conf = conf_sum / boxes     # 平均置信度
    avg_ms = 0.0
    if samples > 0:
        avg_ms = ms_sum / samples       #平均单帧毫秒
    return {"samples":samples, "hit":hit, "rate":rate, "avg_conf":avg_conf, "avg_ms":avg_ms}


rows = []
for wname, wpath in WEIGHTS:  # 外层换权重
    model = YOLO(wpath)
    for vname, vpath in VIDEOS:  # 内层换源
        r = eval_one(model, vpath)  # eval_one 是 qc_video 的量化版 抽样 记命中帧数 置信度总和 耗时总和 最后各除一次得平均
        rows.append((wname, vname, r))  # 权重 源 成绩
        print(wname, "|", vname, "| 命中", r["hit"], "/", r["samples"],
              "| 平均conf", round(r["avg_conf"], 2), "| 平均ms", round(r["avg_ms"], 1) )
    del model

lines = []
lines.append("# 权重选型评测报告")
lines.append("")
lines.append("抽样: 每" + str(STEP) + "帧 | 阈值: " + str(CONF) + " | 硬件: RTX4060")
lines.append("")
lines.append("| 权重 | 视频 | 命中/抽样 | 命中率 | 平均置信度 | 平均单帧ms |")
lines.append("|---|---|---|---|---|---|")
for wname, vname, r in rows:
    lines.append("| " + wname + " | " + vname + " | " + str(r["hit"]) + "/" + str(r["samples"])
                    + " | " + str(round(r["rate"] * 100)) + "%"
                    + " | " + str(round(r["avg_conf"], 2))
                    + " | " + str(round(r["avg_ms"], 1)) + " |")

report_path = os.path.join(settings.BASE_DIR, "docs", "eval_report.md")
f = open(report_path, "w", encoding="utf-8")
for line in lines:
    f.write(line + "\n")
f.close()
print("报告写的路径：", report_path)

























