"""
    这个文件调整项目中的参数
    路径用__file__锚定到项目根目录，不受工作目录影响
"""
import os

#__file__ 本文件自身路径
#abspath() 绝对路径     dirname() 去掉最后一级，往上一级 往上两级刚好到项目根

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# MODEL_PATH = os.path.join(BASE_DIR, "weights", "yolo11m.pt")
MODELS = [
    {"path": os.path.join(BASE_DIR, "weights", "yolo11m.pt"),        "name": "yolo11m 通用80类"},
    {"path": os.path.join(BASE_DIR, "weights", "helmet_yolov8m.pt"), "name": "安全帽 Hardhat/NO-Hardhat"},
    {"path": os.path.join(BASE_DIR, "weights", "fire_smoke_yolov8n.pt"), "name": "火焰烟雾 fire/smoke"},
]

# SOURCE = 0
# SOURCE = "rtsp://admin:qlhk&1111@192.168.8.222:554/1/2"
# SOURCE_KIND = "camera"  # video/camera/rtsp/image

SOURCES = [
    {"kind": "video",  "value": os.path.join(BASE_DIR, "data", "raw", "crowd1.mp4"), "name": "人群视频"},
    {"kind": "video",  "value": os.path.join(BASE_DIR, "data", "raw", "fire.mp4"),  "name": "火焰视频"},
    {"kind": "camera", "value": 0,                                                  "name": "本机摄像头"},
    {"kind": "image", "value": os.path.join(BASE_DIR, "data", "alarms", "alarm_20260930-155938.jpg"), "name":"照片"},
    {"kind": "video", "value": os.path.join(BASE_DIR, "data", "raw", "fireclose1.ogv"), "name": "近景柴火"},
    {"kind": "video", "value": os.path.join(BASE_DIR, "data", "raw", "wildfire1.webm"), "name": "野火航拍"},
    {"kind": "video", "value": os.path.join(BASE_DIR, "data", "raw", "distant1.webm"), "name": "远景山火"},
    {"kind": "video", "value": os.path.join(BASE_DIR, "data", "raw", "factory1.webm"), "name": "厂区产线"},
    {"kind": "video", "value": os.path.join(BASE_DIR, "data", "raw", "factory2.ogv"), "name": "车间内景"},
]

SCENES = [
    {"name": "厂区消防",   "model": 2, "classes": ["fire", "smoke"],  "frames": 3, "conf":0.3},
    {"name": "工地安全帽", "model": 1, "classes": ["NO-Hardhat"],     "frames": 5, "conf":0.4},
    {"name": "人员统计",   "model": 0, "classes": ["person"],         "frames": 5, "conf":0.4},
]

ALARM_DIR = os.path.join(BASE_DIR, "data", "alarms")  # 报警图片记录

DB_PATH = os.path.join(BASE_DIR, "data", "alarms.db")  # 数据库存记录

CONF = 0.4
WINDOW_NAME = "Vision-guard"

WEB_PORT = 5000