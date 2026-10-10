import time

class Perf:
    # 秒表盒子：记每帧耗时，算FPS
    def __init__(self, window=60):
        self.window = window    # 滑动窗口大小，只记最近60帧
        self.dts = []           # 最近每帧耗时的清单，单位秒  delta t s 时间差 复数
        self.frames = 0         # 累计处理帧数 计数器 以后往上边+1
        self.start = time.time() # 程序起跑时间

    # 每帧检测完叫一次，dt是这一帧发的秒数
    def tick(self, dt): # 参数 dt = 调用者递进来的这一帧花了几秒
        self.dts.append(dt)
        if len(self.dts) > self.window:  #假设3>2 然后开始丢最老的那条左边，这样传送带：右边上新，左边掉旧。
            self.dts.pop(0)     #pop(0) = 扔掉下标 0 那条 。 pop() 不带参数扔最后一条
        self.frames = self.frames + 1

    # 窗口内平均每帧耗时(秒)
    def avg_dt(self):
        if len(self.dts) == 0:  # 防止清单为0 ZeroDivisionError 写除法的检查
            return 0.0
        total = 0.0  # 累加器
        for d in self.dts:
            total = total + d
        return total/len(self.dts)  # 计数总秒数/次数=单条平均秒数

    # FPS = 1s / 平均每帧率耗时 平均耗时换成每秒帧数  1秒里能塞几个秒
    def fps(self):
        avg = self.avg_dt()  # 一个方法叫同一只盒子的另一个方法。self. 开头 = "问自己"
        if avg <= 0:
            return 0.0
        return 1.0 / avg

    # 给 jsonify 的快照，键名固定，前端照单收获 拍一张照，递出去
    def snapshot(self):
        recent = []
        for d in self.dts:
            recent.append((round(d * 1000, 1)))  # 秒换算成毫秒 round(数*1000(每条秒换成毫秒), 保留几位小数)
        return {
            "fps":round(self.fps(), 1),  #字典变成 JSON 发给浏览器，JSON 的键必须是字符串
            "ms":round(self.avg_dt() * 1000, 1),
            "frames":self.frames,
            "uptime":int(time.time() - self.start),
            "recent":recent

        }