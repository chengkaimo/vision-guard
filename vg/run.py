import cv2
import settings
import camera
import detector
import alarm
import time
import os
import web
import threading
from scene import Scene
import metrics


def main():
    model = detector.load_model() # 获取模型来源
    cap = camera.open_camera()  # 获取视频源

    alarm.init_db() # 获取数据库
    server = threading.Thread(target=web.start_server, daemon=True)
    server.start()

    scene = Scene(settings.SCENE_NAME, settings.ALARM_CLASSES, settings.ALARM_FRAMES)
    web.bind_scene(scene)

    perf = metrics.Perf()
    web.bind_perf(perf)

    while True:
        t0 = time.time()  # t0是指本帧的起点时刻
        ok, frame = camera.read_frame(cap)
        if not ok:
            print("断流了，3s后重连")
            cv2.waitKey(3000)
            cap.release()
            cap = camera.open_camera()
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

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

