import time

# 共享台账 设置在文件顶层，全模块共用
seen_ids = set()  #set
first_seen = {}  # 首次见到时间 工号 dict
last_seen = {}  # 最后见到时间 工号 dict

def update(found):
    now = time.time()
    for name, conf, tid in found:
        if name != "person":
            continue
        if tid < 0:
            continue
        seen_ids.add(tid)
        last_seen[tid] = now
        if tid not in first_seen:
            first_seen[tid] = now  # 第一次的时间 用于算时间差

def total_person():
    return len(seen_ids)

def long_stayers(seconds):
    count = 0
    for tid in seen_ids:
        if last_seen[tid] - first_seen[tid] >=seconds:
            count += 1

    return count

