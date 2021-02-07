![Image Text](https://github.com/Harpes/ChloeBot/blob/master/nodeweb/public/chloe.gif?raw=true)

# ChloeBot

A QQBot based on Nonebot for PCR clanbattle

基于 [NoneBot 1.x](https://nonebot.cqp.moe/)框架的 pcr 公会战特化的 QQ 机器人

## 部署指南 - QuickStart

1. 获取下列资源

    - Python3 https://www.python.org/
    - NodeJs https://nodejs.org/ & yarn (`npm install -g yarn`)
    - go-cqhttp https://github.com/Mrs4s/go-cqhttp

2. 运行 go-cqhttp 并修改配置文件，下面的配置可供参考：

    ```json
    ws_reverse_servers: [
        {
            "enabled": true,
            "reverse_url": "ws://127.0.0.1:8080/ws/",
            "reverse_api_url": "ws://127.0.0.1:8080/ws/api/",
            "reverse_event_url": "ws://127.0.0.1:8080/ws/event/",
            "reverse_reconnect_interval": 3000
        }
    ]
    ```

3. 进入本项目的根目录，确认下列的 Python 依赖库已安装：

    - nonebot nonebot[scheduler]
    - requests
    - pillow
    - zhconv
    - quart_compress

4. 最后，开启两个命令行窗口，其中一个运行 `main.py` ，另一个 `cd nodeweb && yarn && yarn start`

## 公会战指令

##### 公会战命令全部需要在群内使用，请注意命令中的空格，方括号[]表示命令中的可选项

-   初次使用时，需要设置公会名与服务器地区（需要群主权限）：

    ```
    创建国服公会 <公会名>
    创建台服公会 <公会名>
    创建日服公会 <公会名>
    ```

    如在会战开始前需要重置会战进度，使用 `重置进度` 命令然后按照 bot 的答复回复即可。

-   报刀/代报刀：

    ```
    报刀 <伤害值>
    <@某人> <伤害值>
    尾刀 [@某人]
    <@某人> 尾刀
    ```

    不小心报错刀以后，还可以使用 `撤销` 命令取消上一条出刀记录。

    \*可选：除此之外，bot 还能够计算尾刀的返还时间，使用命令：

    ```
    报刀 <伤害值> [剩余时间s]
    <@某人> <伤害值> [剩余时间s]
    ```

    能让 bot 自动记录尾刀的返还时间，方便公会管理安排尾刀。

-   预约/取消预约 `预约<Boss编号>` / `取消<Boss编号>`：

    ```
    预约1
    取消2
    预约查询
    ```

    也可以使用`预约查询`查询当前各个 Boss 的预约情况。

-   出刀状态记录：

    使用`申请出刀` / `我进了`指令记录 Boss 的进入情况，或者使用 `暂停` 指令记录一些信息，方便进行合刀操作。

    ```
    申请出刀
    暂停 699w 4s [...]
    ```

    如不小心误操作，可以使用 `取消出刀` 指令清除上面记录的信息，或者等待 Boss 击杀以后自动清除。

-   简单的 `挂树` 指令

    ```
    挂树
    上树
    ```

-   其他指令

    `状态` / `会战进度` `查尾刀` `每日报告`

## 友情链接

**干炸里脊资源站**: https://redive.estertion.win/

**公主连结 Re: Dive Fan Club - 硬核的竞技场数据分析站**: https://pcrdfans.com/

**yobot**: https://yobot.win/

**HoshinoBot**: https://github.com/Ice-Cirno/HoshinoBot
