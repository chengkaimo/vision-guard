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
    ("远景山火", os.path.join(settings.BASE_DIR, "data", "raw", "distant1.webm")),
    ("极远景烟", os.path.join(settings.BASE_DIR, "data", "raw", "distant2.webm")),
    ("厂区产线", os.path.join(settings.BASE_DIR, "data", "raw", "factory1.webm")),
    ("车间内景", os.path.join(settings.BASE_DIR, "data", "raw", "factory2.ogv")),
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
    kinds = {}  # 类别计数器：名字→出现次数
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
            cname = results[0].names[int(b.cls[0])]  # 编号→名字
            kinds[cname] = kinds.get(cname, 0) + 1  # 这个名字计数+1
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
    return {"samples":samples, "hit":hit, "rate":rate, "avg_conf":avg_conf, "avg_ms":avg_ms, "kinds": kinds}


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
lines.append("")
lines.append("## 结论")
lines.append("")
lines.append("1.每个视频的最佳权重")
for vname, vpath in VIDEOS:
    best_name = ""
    best_rate = -1.0
    for wn, vn, r in rows:
        if vn == vname and r["rate"] > best_rate:
            best_rate = r["rate"]
            best_name = wn
    lines.append("- " + vname + ": 最佳 " + best_name + "（命中率 " + str(round(best_rate * 100)) + "%）")
lines.append("2.每只权重认不出什么")
for wname, wpath in WEIGHTS:
    blind = []
    for wn, vn, r in rows:
        if wn == wname and r["rate"] == 0.0:
            blind.append(vn)
    if len(blind) == 0:
        lines.append("-" + wname + "：本次所有的视频都可以认得出来")
    else:
        lines.append("-" + wname + "：认不出来" + "/".join(blind))
lines.append("3.误检测清单")
MIS = ["厂区产线", "车间内景", "人群对照"]
for wn, vn, r in rows:
    if vn in MIS and len(r["kinds"]) > 0:
        kinds = dict(r["kinds"])        # 抄一份副本，删的时候不动原来的
        top = []
        for _ in range(3):              # 选三轮：top1, top2, top3
            if len (kinds) == 0:
                break
            bk = ""
            bv = -1
            for k in kinds:
                if kinds[k] > bv:
                    bv = kinds[k]
                    bk = k
            top.append(bk + "x" + str(bv))
            del kinds[bk]               # top1退场 下一轮top2才能进来
        lines.append("- " + wn + " 在 " + vn + " 检的最多" + ", ".join(top))




report_path = os.path.join(settings.BASE_DIR, "docs", "eval_report.md")
# # 加个已经存在文件不覆盖的判断
# i = 1
# while os.path.exists(report_path):
#     report_path = os.path.join(settings.BASE_DIR, "docs", f"eval_report_{i}.md")
#     i += 1

f = open(report_path, "w", encoding="utf-8")
for line in lines:
    f.write(line + "\n")
f.close()
print("报告写的路径：", report_path)

