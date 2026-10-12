import cv2
import os

class Source:
    # 视频源盒子 不管哪种源，对外只会read()拿出一帧
    def __init__(self, kind, value):
        self.kind = kind        # video/camera/rtsp/image
        self.value = value      # 路径/编号/网址
        self.cap = None         # 视频和摄像头才用得上
        self.frame = None       # 图片源用，读一次，之后反复交同一张

    # 按kind用不同方式打开源
    def open(self):
        if self.kind == "video":
            self.cap = cv2.VideoCapture(self.value)
        elif self.kind == "camera":
            self.cap = cv2.VideoCapture(int(self.value), cv2.CAP_DSHOW)
        elif self.kind == "rtsp":
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;tcp"  # 环境变量键值对 FFmpeg 走 TCP
            self.cap = cv2.VideoCapture(self.value)
        elif self.kind == "image":
            self.frame = cv2.imread(self.value)
        else:
            print("没有匹配的源，不认识的SOURCE_KIND：", self.kind)
        return self.is_ok()

    # 开没开成功
    def is_ok(self):
        if self.kind == "image":
            return self.frame is not None
        return self.cap is not None and self.cap.isOpened()

    # 对外唯一动作 拿一帧
    def read(self):
        if self.kind == "image":
            if self.frame is None:
                return False, None
            return True, self.frame
        ok, frame = self.cap.read()
        if not ok and self.kind == "video":  # CAP_PROP_POS_FRAMES 是 OpenCV predefined 的常量名（属性：当前帧号）
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # 视频放完，播放指针回到0帧，倒回开头循环播
            ok, frame = self.cap.read()
        return ok, frame

    #关掉：把内容清空
    def release(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None  # 把引用清空，确认cap死对象不会后续在is_ok()问在不在


    def label(self):
        return self.kind + ":" + str(self.value)

