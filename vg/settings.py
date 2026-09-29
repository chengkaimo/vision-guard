"""
    这个文件调整项目中的参数
    路径用__file__锚定到项目根目录，不受工作目录影响
"""
import os

#__file__ 本文件自身路径
#abspath() 绝对路径     dirname() 去掉最后一级，往上一级 往上两级刚好到项目根

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "weights", "yolo11m.pt")
SOURCE = os.path.join(BASE_DIR, "data", "raw", "crowd1.mp4")
# SOURCE = 0
# SOURCE = "rtsp://admin:qlhk&1111@192.168.8.222:554/1/2"

SCENE_NAME = ["厂区安全监控"]
ALARM_CLASSES = ["fire", "smoke", "light","person"]  # 触发警报的类
ALARM_FRAMES = 5  # 消抖帧数
ALARM_DIR = os.path.join(BASE_DIR, "data", "alarms")  # 报警图片记录

DB_PATH = os.path.join(BASE_DIR, "data", "alarms.db")  # 数据库存记录

CONF = 0.4
WINDOW_NAME = "Vision-guard"

WEB_PORT = 5000