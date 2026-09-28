
from flask import Flask
import sqlite3
import cv2
import os
import config
import stats

app = Flask(__name__)

#共享画板：main 工人每帧更新，直播工人每刻来取
LATEST = {"vis":None}

def start_server():
    # 服务器工人站前台：0.0.0.0允许局域网访问
    app.run(host="0.0.0.0", port=config.WEB_PORT, threaded=True)

@app.route("/")
def index():
    # 首页
    return ' <h1>Monitor</h1> <img src="/video" style="max-width:100%"> <p><a href="/history">报警历史</a><a href="/stats">人数统计</a></p> '

@app.route("/video")
def video():
    def gen():
        while True:
            vis = LATEST["vis"]
            if vis is None:  # 如果画板是空的 那就跳出循环进入下一轮循环 等到main工人挂上 才继续
                continue
            jpg = cv2.imencode(".jpg", vis)[1].tobytes()
            yield(b"--frame\r\nContent-Type:image/jpeg\r\n\r\n" +jpg+  b"\r\n")
    from flask import Response
    return Response(gen(),mimetype="multipart/x-mixed-replace;boundary=frame")

@app.route("/history")
def history():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute("select id, time, class_name, conf, image_path FROM alarms ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    #HTML就是字符串：一行行拼出表格
    html = "<h1>报警历史</h1> <table border=1>"
    html = html + "<tr> <th>ID</th><th>时间</th><th>类别</th><th>置信度</th><th>证据</th> </tr>"  # ID/时间/类别/置信度/证据

    for row in rows:
        fname = os.path.basename(row[4])
        html = html + "<tr><td>" + str(row[0]) + "</td><td>" + row[1] + "</td><td>" + row[2] + "</td><td>" + str(round(row[3], 2)) + "</td><td><img src='/pic/" + fname + "' width=240></td></tr>"
    html = html + "</table>"
    return html

@app.route("/pic/<name>")
def pic(name):
    path = os.path.join(config.ALARM_DIR, name)
    from flask import send_file
    return send_file(path)

@app.route("/stats")
def stats_page():
    html = "<h1>人数统计</h1>"
    html = html + "<p>累计经过人数"+ str(stats.total_person()) + "</p>"
    html = html + "<p>停留超10s人数：" + str(stats.long_stayers(10)) + "</p>"
    html = html + '<p><a href="/">回直播</a> | <a href="/history">报警历史</a></p>'
    return html
