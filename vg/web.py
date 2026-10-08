import time
from flask import Flask
from flask import render_template
from flask import jsonify  # 把字典变成JSON的工具
import sqlite3
import cv2
import os
import settings

app = Flask(__name__)

#共享画板：main 工人每帧更新，直播工人每刻来取
LATEST = {"vis":None, "scene":None, "perf":None}
def bind_scene(scene):
    LATEST["scene"] = scene
def bind_perf(perf):
    LATEST["perf"] = perf

def start_server():
    # 服务器工人站前台：0.0.0.0允许局域网访问
    app.run(host="0.0.0.0", port=settings.WEB_PORT, threaded=True)

@app.route("/")
def index():
    # 首页
    scene = LATEST["scene"]
    if scene is None:
        return render_template("home.html", scene_name="视频还没上线", alarm_list="-", page_title="直播")

    return render_template(
        "home.html",
        scene_name = scene.name,       # 场景名只是个贴纸，不参与逻辑
        alarm_list = "/".join(scene.alarm_classes),
        page_title = "直播"
    )


@app.route("/video")
def video():
    def gen():
        start_empty = time.time()  #不能放while里，否则每圈重新记时，时间差算不对
        while True:
            vis = LATEST["vis"]
            if vis is None:  # 如果画板是空的 那就跳出循环进入下一轮循环 等到main工人挂上才继续
                if time.time() - start_empty > 60:  # 空等超过60秒，收线下班
                    break
                time.sleep(0.05)        # 空等要睡觉，不能空转
                continue
            jpg = cv2.imencode(".jpg", vis)[1].tobytes()
            yield(b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" +jpg+  b"\r\n")
    from flask import Response
    return Response(gen(),mimetype="multipart/x-mixed-replace;boundary=frame")

@app.route("/history")
def history():
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select id, time, class_name, conf, image_path FROM alarms ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    # 元组->字典->列表
    records = []  # 列表List
    for row in rows:  # # ID/时间/类别/置信度/证据
        record = {}  # 字典
        record["id"] = row[0]
        record["time"] = row[1]
        record["class_name"] = row[2]
        record["conf"] = round(row[3], 2)  # 置信度是浮点数 数据在python里先round()处理好四舍五入
        record["pic"] = os.path.basename(row[4])  # basename返回文件名 只取文件名
        records.append(record)  # 把字典的数据加入到列表里record->records

    return render_template("history.html", records = records, count = len(records), page_title="报警历史")


@app.route("/pic/<name>")
def pic(name):
    path = os.path.join(settings.ALARM_DIR, name)
    from flask import send_file
    return send_file(path)

@app.route("/stats")
def stats_page():
    # 从画板取盒子
    scene = LATEST["scene"]
    if scene is None:
        return render_template("stats.html", total=0, seconds=10, stayers=0,online=False, page_title="人数统计")

    return render_template(
        "stats.html",
        total=scene.total_persons(),
        stayers=scene.long_stayers(10),
        seconds=10,
        page_title="人数统计",
        online = True
    )

# 原始数据的接口
@app.route("/api/stats")
def api_stats():
    scene = LATEST["scene"]
    if scene is None:
        return jsonify({"online":False, "total": 0, "stayers": 0, "seconds":10})

    return jsonify(
        {
            "online":True,
            "total":scene.total_persons(),
            "stayers":scene.long_stayers(10),
            "seconds": 10
        }
    )

@app.route("/api/metrics")
def api_metrics():
    perf = LATEST["perf"]
    if perf is None:
        return jsonify({"online":False, "fps": 0, "ms": 0, "frames":10,"uptime":0,"recent":[]})
    data = perf.snapshot()
    data["online"] = True
    return jsonify(data)

@app.route("/metrics")
def metrics_page():
    return render_template("metrics.html", page_title="性能仪表盘")
