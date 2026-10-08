import time

class Perf:
    # 秒表盒子：记每帧耗时，算FPS
    def __init__(self, window=60):
        self.window = window    # 滑动窗口大小，只记最近60帧
        self.dts = []           # 最近每帧耗时的清单，单位秒
        self.frames = 0         # 累计处理帧数
        self.start = time.time() # 程序起跑时间

    # 每帧检测完叫一次，dt是这一帧发的秒数
    def tick(self, dt):
        self.dts.append(dt)
        if len(self.dts) > self.window:
            self.dts.pop(0)     #窗口填满了 扔掉最老那条
        self.frames = self.frames + 1

    # 窗口内平均每帧耗时(秒)
    def avg_dt(self):
        if len(self.dts) == 0:
            return 0.0
        total = 0.0
        for d in self.dts:
            total = total + d
        return total/len(self.dts)

    # FPS = 1s / 平均每帧率耗时
    def fps(self):
        avg = self.avg_dt()
        if avg <= 0:
            return 0.0
        return 1.0 / avg

    # 给 jsonify 的快照，键名固定，前端照单收获
    def snapshot(self):
        recent = []
        for d in self.dts:
            recent.append((round(d * 1000, 1)))  # 秒换算成毫秒
        return {
            "fps":round(self.fps(), 1),
            "ms":round(self.avg_dt() * 1000, 1),
            "frames":self.frames,
            "uptime":int(time.time() - self.start),
            "recent":recent

        }