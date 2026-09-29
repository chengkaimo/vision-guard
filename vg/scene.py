import time


class Scene:
    # 场景出生登记
    def __init__(self, name, alarm_classes, alarm_frames):
        self.name = name                        #场景名
        self.alarm_classes = alarm_classes      #场景里的报警名单
        self.alarm_frames = alarm_frames        #场景里的消抖帧数
        self.seen_ids = set()                   #见过的工号篮子（自动去重）
        self.first_seen = {}                    #第一次记录
        self.last_seen = {}                     #最后一次记录
        self.hit_count = 0                      #消抖计数器

    # 功能： 只看本帧登记表，更新表+消抖判断 通知是否报警
    # ps：只判断不存档——判断归办事的，动手归run 职责分工
    def update(self, found):
        now = time.time()
        for name, conf, tid in found:
            if name == "person" and tid >= 0:
                self.seen_ids.add(tid)
                self.last_seen[tid] = now
                if tid not in self.first_seen:
                    self.first_seen[tid] = now

        # 开始判断本帧有没有报警类目标
        alarm_now = False
        alarm_name = ""
        alarm_conf = 0.0
        for name, conf, tid in found:
            if name in self.alarm_classes:
                alarm_now = True
                alarm_name = name
                alarm_conf = conf
        # 消抖：连续命中好几帧才给亮报警一次
        if alarm_now:
            self.hit_count += 1
        else:
            self.hit_count = 0
        fire = (self.hit_count == self.alarm_frames)
        return fire, alarm_name, alarm_conf


    def total_persons(self):
        return len(self.seen_ids)

    def long_stayers(self, seconds):
        count = 0
        for tid in self.seen_ids:
            if self.last_seen[tid] - self.first_seen[tid] >= seconds:
                count += 1

        return count

