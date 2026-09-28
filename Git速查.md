# Git 常用指令速查表（vision-guard 版）

> 语法模板：git push 到〈哪儿 origin〉〈什么 main〉。所有命令在仓库目录内执行（cd 到 vision-guard）。

## 一、一次性配置（换电脑才需要重做）

| 命令 | 干什么 | 注意 |
|---|---|---|
| git config --global user.name "显示名" | 存档签名，随便起 | 中文也行，不必等于GitHub用户名 |
| git config --global user.email "邮箱" | **必须与GitHub注册邮箱一致**，否则commit不挂头像 | 一次性 |
| git config --global --list | 检查当前配置 | 随时可查 |

## 二、日常四件套（每天用，形成肌肉记忆）

```powershell
git status              # ① 问诊：现在什么状态(改了什么/背包里有什么)
git add .               # ② 装包：所有改动放进暂存区(尊重.gitignore)
git commit -m "干了什么" # ③ 存档：留言要具体,"修复消抖重复入库"优于"update"
git push                # ④ 上云：首次或换仓库后需 git push -u origin main
```

单文件装包：`git add 文件名`（只背包里放这一个）。

## 三、查看历史

| 命令 | 干什么 |
|---|---|
| git log --oneline | 存档列表一行一个（最常用） |
| git log | 完整存档详情（按 q 退出） |
| git diff | 还没 add 的改动具体是哪几行 |
| git remote -v | 云端地址外号对照表 |

## 四、撤销三档（从轻到重，看清再用）

| 场景 | 命令 | 后果 |
|---|---|---|
| 改了文件没 add，想丢弃改动 | git restore 文件名 | **该文件改动丢失**，不可逆 |
| add 多了，想从背包拿出 | git restore --staged 文件名 | 改动还在，只是不本次存档 |
| commit 留言写错（没 push 前） | git commit --amend -m "新留言" | 只改最后一次存档 |

## 五、云端与取货

| 命令 | 干什么 |
|---|---|
| git clone 仓库地址 | 把别人的仓库整个下载到本地（GitHub 项目学习第一步） |
| git pull | 云端有新存档拉下来（多设备同步/提示 rejected 时先跑它） |
| git remote set-url origin 新地址 | 换云端地址（账号搞错时用过的） |

## 六、.gitignore 规矩（放进仓库的黑名单）

每行一个模式：`目录/` `*.pt` `*.db` `.venv/` `__pycache__/`。
原则：**可重建的不存（环境）、超100MB的不存（权重）、隐私不存（报警人脸数据）**。

## 七、常见报错速查

| 报错关键词 | 人话 | 处置 |
|---|---|---|
| Permission to X denied to Y | 钥匙和锁不配对（两个账号混了） | 凭据管理器删 git:https://github.com 重登对账号 |
| rejected ... fetch first | 云端有你本地没有的存档 | git pull 后再 git push |
| unrecognized argument | 参数拼写错 | 看本表核对（--oneline 不是 --online） |
| Please tell me who you are | 没配 user.name/email | 回到第一节配置 |
| Failed to connect / timeout | 网络到 GitHub 不畅 | 重试几次；换手机热点；检查代理 |

## 八、分支（阶段2前了解即可，暂不用）

存档线概念：main 是主干；`git branch 名字` 造新线，`git switch 名字` 换线。
单人项目前期一条 main 走天下，功能开发多了再学分支不迟。
