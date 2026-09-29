import cv2
import settings
import camera
import detector
import alarm
import time
import os
import web
import threading
import stats

def main():
    model = detector.load_model() # 获取模型来源
    cap = camera.open_camera()  # 获取视频源

    alarm.init_db() # 获取数据库
    server = threading.Thread(target=web.start_server, daemon=True)
    server.start()

    hit_count = 0  # 消框抖计数器
    while True:
        ok, frame = camera.read_frame(cap)
        if not ok:
            print("断流了，3s后重连")
            cv2.waitKey(3000)
            cap.release()
            cap = camera.open_camera()
            continue

        # vis, found = detector.detect(model, frame)
        vis, found = detector.detect_track(model, frame)
        stats.update(found)

        cv2.imshow(settings.WINDOW_NAME, vis)

        web.LATEST["vis"] = vis  # 画板 画好的vis挂上共享画板

        # 判断当前帧是否命中报警类：遍历found，顺带把名字和置信度带出来
        alarm_now = False
        alarm_name = ""
        alarm_conf = 0.0
        for name, conf, cid in found:
            if name in settings.ALARM_CLASSES:
                alarm_now = True
                alarm_name = name
                alarm_conf = conf

        # 消抖计数：命中＋1，没命中归零
        if alarm_now:
            hit_count += 1
        else:
            hit_count = 0

        # 连续N（5）帧才入库
        if hit_count == settings.ALARM_FRAMES:
            stamp = time.strftime("%Y%m%d-%H%M%S")  # 时间戳 待会用来当文件名就不会重名保存覆盖了
            image_path = os.path.join(settings.ALARM_DIR, "alarm_" + stamp + ".jpg")
            cv2.imwrite(image_path, vis)
            alarm.save_alarm(alarm_name, alarm_conf, image_path)
            print("报警入库", alarm_name)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

