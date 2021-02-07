import React from 'react';
import ReactMarkdown from 'react-markdown';

const DOCS = `## 公会战指令

##### 公会战命令全部需要在群内使用，请注意命令中的空格，方括号[]表示命令中的可选项

-   初次使用时，需要设置公会名与服务器地区（需要群主权限）：

    \`\`\`
    创建国服公会 <公会名>
    创建台服公会 <公会名>
    创建日服公会 <公会名>
    \`\`\`

    如在会战开始前需要重置会战进度，使用 \`重置进度\` 命令然后按照 bot 的答复回复即可。

-   报刀/代报刀：

    \`\`\`
    报刀 <伤害值>
    <@某人> <伤害值>
    尾刀 [@某人]
    <@某人> 尾刀
    \`\`\`

    不小心报错刀以后，还可以使用 \`撤销\` 命令取消上一条出刀记录。

    \\*可选：除此之外，bot 还能够计算尾刀的返还时间，使用命令：

    \`\`\`
    报刀 <伤害值> [剩余时间s]
    <@某人> <伤害值> [剩余时间s]
    \`\`\`

    能让 bot 自动记录尾刀的返还时间，方便公会管理安排尾刀。

-   预约/取消预约 \`预约<Boss编号>\` / \`取消<Boss编号>\`：

    \`\`\`
    预约1
    取消2
    预约查询
    \`\`\`

    也可以使用\`预约查询\`查询当前各个 Boss 的预约情况。

-   出刀状态记录：

    使用\`申请出刀\` / \`我进了\`指令记录 Boss 的进入情况，或者使用 \`暂停\` 指令记录一些信息，方便进行合刀操作。

    \`\`\`
    申请出刀
    暂停 699w 4s [...]
    \`\`\`

    如不小心误操作，可以使用 \`取消出刀\` 指令清除上面记录的信息，或者等待 Boss 击杀以后自动清除。

-   简单的 \`挂树\` 指令

    \`\`\`
    挂树
    上树
    \`\`\`

-   其他指令

    \`状态\` / \`会战进度\` \`查尾刀\` \`每日报告\`
`;

const HomePage = () => {
    return (
        <>
            <img
                src="https://raw.githubusercontent.com/Harpes/ChloeBot/master/nodeweb/public/chloe.gif"
                width={500}
                height={500}
            />
            <ReactMarkdown source={DOCS} />
        </>
    );
};

export default HomePage;
