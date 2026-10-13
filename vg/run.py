import cv2
import settings
import detector
import alarm
import time
import os
import web
import threading
from scene import Scene
import metrics
from source import Source


def main():
    # model = detector.load_model() # 获取模型来源
    first_model = settings.MODELS[0]
    model = detector.load(first_model["path"])  # settings.MODELS[0]["path"]
    web.LATEST["model_label"] = first_model["name"]
    print("当前类别表：", model.names)  # model.names是类别表 字典 编号→名字

    first = settings.SOURCES[0]
    src = Source(first["kind"], first["value"])
    if not src.open():
        print("源打不开：", src.label())
        return  # 开不了就打印名字，然后下班退出main()，不进循环，拦截
    web.LATEST["source_label"] = src.label()

    alarm.init_db() # 获取数据库
    server = threading.Thread(target=web.start_server, daemon=True)
    server.start()

    # scene = Scene(settings.SCENE_NAME, settings.ALARM_CLASSES, settings.ALARM_FRAMES)
    # web.bind_scene(scene)
    pack = settings.SCENES[0]  # 场景包0号
    m = settings.MODELS[pack["model"]]  # 模型包[场景包0号的模型健→值为0 取下标为0的模型 yolo11m的80类]
    model = detector.load(m["path"])
    scene = Scene(pack["name"], pack["classes"], pack["frames"])
    web.bind_scene(scene)
    web.LATEST["model_label"] = m["name"]
    web.LATEST["scene_label"] = pack["name"]
    print("当前场景：", pack["name"], "类别表",model.names)

    perf = metrics.Perf()
    web.bind_perf(perf)

    while True:
        pending = web.take_pending_source()  # 换源
        if pending is not None:
            kind, value = pending   #二元组拆包
            src.release()
            src = Source(kind, value)
            if src.open():
                web.LATEST["source_label"] = src.label()
                print("已换源：", src.label())
            else:
                print("换源失败：", src.label())
            continue        # 本圈只干换源这一件事 换源这一圈不检测 不要计时不准的假数据

        pending_model = web.take_pending_model()  # 换权重
        if pending_model is not None:
            m = settings.MODELS[pending_model]
            del model                                   # 卸掉旧的模型，腾出点显存空间
            model = detector.load(m["path"])
            web.LATEST["model_label"] = m["name"]
            print("已经换了权重：", m["name"])
            print("新的类别表：", model.names)
            continue                                    # 同上 加载这几秒不记时不检测

        pending_scene = web.take_pending_scene()
        if pending_scene is not None:
            pack = settings.SCENES[pending_scene]
            m = settings.MODELS[pack["model"]]
            del model
            model = detector.load(m["path"])
            scene = Scene(pack["name"], pack["classes"], pack["frames"])    # 新场景 = 新账本
            web.bind_scene(scene)
            web.LATEST["model_label"] = m["name"]
            web.LATEST["scene_label"] = pack["name"]
            print("已经切换场景：", pack["name"], "类别表：", model.names)
            continue


        t0 = time.time()  # t0是指本帧的起点时刻
        ok, frame = src.read()
        if not ok:
            print("断流了，3s后重连")
            cv2.waitKey(3000)
            src.release()
            src.open()
            continue

        vis, found = detector.detect_track(model, frame)

        cv2.imshow(settings.WINDOW_NAME, vis)
        web.LATEST["vis"] = vis  # 画板 画好的vis挂上共享画板

        fire, alarm_name, alarm_conf = scene.update(found)

        if fire:
            stamp = time.strftime("%Y%m%d-%H%M%S")  # 时间戳 来当文件名就不会重名保存覆盖了
            image_path = os.path.join(settings.ALARM_DIR, "alarm_" + stamp + ".jpg")
            cv2.imwrite(image_path, vis)
            alarm.save_alarm(alarm_name, alarm_conf, image_path)
            print("报警入库", alarm_name)

        perf.tick(time.time() - t0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    src.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

