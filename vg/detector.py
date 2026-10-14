"""
    这个文件负责检测
"""

from ultralytics import YOLO
import settings

def load(path):
    return YOLO(path)
def load_model():
    model = load(settings.MODELS)
    return model

def detect(model, frame):
    results = model.predict(frame, conf=settings.CONF, verbose=False)
    result = results[0]
    # vis = model.plot(de)[0]
    vis = result.plot()

    names = result.names
    found = []
    for box in result.boxes:
        cid = int(box.cls[0])
        name = names[cid]
        conf = float(box.conf[0])
        found.append((name, conf))

    return vis, found # 返回 画好的图vis给屏幕 登记表found给报警逻辑

def detect_track(model, frame, conf):
    results = model.track(frame, conf=conf, persist=True, verbose=False)  # persist记住上一帧
    result = results[0]
    vis = result.plot()
    names = result.names
    found = []
    for box in result.boxes:  # .boxes是框清单 一帧检到几个目标 清单里就有几个box
        cid = int(box.cls[0])  # box是个口袋 .cls装类别编号
        name = names[cid]
        conf = float(box.conf[0])
        tid = -1  # -1代表无工号
        if box.id is not None:  # .id是跟踪工号 没开track时工号就为None
            tid = int(box.id[0])
        # found.append(name, conf, tid) #❌ append一次只能塞一个 要塞三个要打包成元组形式(())
        found.append((name, conf, tid))

    return vis, found