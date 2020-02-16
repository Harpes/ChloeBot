# ChloeBot

A QQBot based on Nonebot for PCR

## 快速指南 - QuickStart

会战部分的功能使用了 [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) 的 clanbattle 插件

#### 会战开始前 - Before Clanbattle

**Step 1:** 邀请机器人至群聊；

**Step 2:** 给群添加一个公会：

```
add-clan --name 鼬鼬美食殿
```

这个命令将会将“鼬鼬美食殿”注册为本群的 1 会，您可以使用自己想用的公会名；

**Step 3:** 通知群员加入公会，每个人使用下面的命令：

```
join-clan --name 祐树
```

这个命令将会将命令发送者加入本群的 1 会，注册昵称为“祐树”，群员可以使用自己的游戏昵称。

---

#### 会战日 - Clanbattle Days

**Step 1 (Optional):** 预约想要挑战的 Boss _本功能正在绝赞开发中..._

**Step 2 (Recommand):** 正式战前进入挑战队列 _本功能正在绝赞开发中..._

**Step 3:** 上报伤害

简易版命令（**学不会命令行？**那就记住这个就好了）：

```
刀 114w r8 b1
```

该命令将会为发送者记录下挑战伤害：对第 8 周目的 Boss1 造成了 1,140,000 点伤害（请修改为实际的参数）

完整功能版命令：

```
dmg 1919810 -r11 -b4 --last
```

该命令将会为发送者记录下挑战伤害：对第 11 周目的 Boss4 造成了 1,919,810 点伤害，收掉尾刀（请修改为实际的参数）

关于`dmg`命令的详细说明请见下方[支持命令一览]节，完整的参数及相关说明为：

```
dmg -r -b damage [--uid] [--alt] [--ext | --last | --timeout]
```

-   r/round: 周目数
-   b/boss: Boss 编号
-   ext/last/timeout: 补时刀/尾刀/掉刀 标志，仅能指定其中一种
-   uid: 上报对象的 QQ 号（用于为他人代报）
-   alt: 上报对象的小号编号

---

#### 会战日结束 - End of a Clanbattle Day

**让我来看看哪个幸运儿还没有出刀：** `show-remain` 查询本会余刀情况；

**一键催刀：** 管理员使用`show-remain`会自动 at 有余刀的成员，提醒其出刀；_私聊催刀绝赞开发中..._

**谁是分奴？谁是弟弟？：** `stat` 查看本会分数排名；

## 支持命令一览

_SUPERUSER 不受权限控制影响_

### 公会管理

| 进度 | 命令      | 参数             | 权限         | 说明                                                                          |
| ---- | --------- | ---------------- | ------------ | ----------------------------------------------------------------------------- |
| ok   | add-clan  | [--cid][--name]  | GROUP_ADMIN  | 添加新公会，编号为 id，默认为该群最大公会 id+1，若无公会则为 1；name 为公会名 |
| ok   | list-clan | (empty)          | GROUP_MEMBER | 默认显示当前 QQ 群的所有公会；--all 显示管理的所有公会，仅 SUPERUSER 可用     |
|      | mod-clan  | --cid --new_name | GROUP_ADMIN  | 修改公会的 name                                                               |
|      | del-clan  | --cid            | GROUP_ADMIN  | 删除公会                                                                      |

### 成员管理

| 进度 | 命令                   | 参数                           | 权限                | 说明                                                                                                                    |
| ---- | ---------------------- | ------------------------------ | ------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| ok   | add-member / join-clan | [--cid][--uid] [--alt][--name] | GROUP_MEMBER        | 将[uid]的小号[alt]加入[cid]会，游戏内 ID 为[name]。参数缺省时将会将命令发送者的大号加入 1 会，自动获取群名片作为 name。 |
| ok   | list-member            | [--cid]                        | GROUP_MEMBER        | 列出[cid]会的成员。默认为 1 会                                                                                          |
|      | mod-member             | [--uid][--alt] --name          | OWNER / GROUP_ADMIN | 修改名称                                                                                                                |
| ok   | del-member / quit-clan | [--uid][--alt]                 | OWNER / GROUP_ADMIN | 退出公会 / 删除成员                                                                                                     |

### Boss 信息查询

### 出刀管理

| 进度 | 命令            | 别名      | 参数                                 | 权限                     | 说明                                                                      |
| ---- | --------------- | --------- | ------------------------------------ | ------------------------ | ------------------------------------------------------------------------- |
| ok   | add-challenge   | dmg       | --round --boss damage [--uid][--alt] | GROUP_MEMBER             | 报刀。[uid]的帐号[alt]对[round]周目第[boss]个 Boss 造成了[damage]点伤害。 |
| ok   | add-challenge-e | dmge / 刀 | r? b? 伤害数字                       | GROUP_MEMBER             | 简易报刀。例，对 5 周目老 4 造成了 1919810 点伤害：dmge 1919810 r5 b4     |
|      | mod-challenge   | mod-dmg   |                                      | GROUP_ADMIN / 记录所有者 | 改刀                                                                      |

### 预约/排队

| 进度 | 命令        | 别名          | 参数 | 权限         | 说明                  |
| ---- | ----------- | ------------- | ---- | ------------ | --------------------- |
| ok   | reserveX    | 预约 X 王     |      | GROUP_MEMBER | 预约 boss，到达时提醒 |
| ok   | unreserveX  | 取消预约 X 王 |      | GROUP_MEMBER | 取消预约 boss         |
| ok   | see_reserve | 查询预约      |      | GROUP_MEMBER | 查看 boss 的预约情况  |
|      | enqueue     | enq / 入队    |      | GROUP_MEMBER | 进入出刀队列          |
|      | dequeue     | deq / 出队    |      | GROUP_MEMBER | 退出出刀队列          |

### 会战统计

| 进度 | 命令        | 参数                     | 权限         | 说明                                       |
| ---- | ----------- | ------------------------ | ------------ | ------------------------------------------ |
| ok   | show-remain | [--cid]                  | GROUP_MEMBER | 查看今日余刀，管理员调用时将进行一键催刀。 |
| ok   | stat        | [--cid]                  | GROUP_MEMBER | 当月会战分数统计，按分数排名               |
|      | plot        | [--cid][--today] [--all] |              | 绘制会战分数报表                           |
