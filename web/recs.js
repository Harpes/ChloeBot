function toThousands(num) {
    var num = (num || 0).toString(),
        result = '';
    while (num.length > 3) {
        result = ',' + num.slice(-3) + result;
        num = num.slice(0, num.length - 3);
    }
    if (num) {
        result = num + result;
    }
    return result;
}
function getBossName(r, b) {
    const stage = r > 34 ? 'D' : r > 10 ? 'C' : r > 3 ? 'B' : 'A';
    return stage + b;
}
function dataDesensitization(uidStr) {
    const numStr = atob(uidStr);
    const len = numStr.length;
    if (len > 4) {
        return numStr.substring(0, 2) + '*' + numStr.substring(len - 3, len);
    }
    return numStr;
}

function renderItem(params, api) {
    const [index, start, end, dmg] = [0, 1, 2, 3].map(i => api.value(i));
    const x = api.coord([index, start])[0];
    const y = api.coord([index, end])[1];
    const [width, height] = api.size([1, -dmg]);

    const rectShape = echarts.graphic.clipRectByRect(
        {
            x: x - width * 0.3,
            y,
            width: width * 0.6,
            height,
        },
        {
            x: params.coordSys.x,
            y: params.coordSys.y,
            width: params.coordSys.width,
            height: params.coordSys.height,
        }
    );

    return (
        rectShape && {
            type: 'rect',
            shape: rectShape,
            style: api.style(),
        }
    );
}

const group = window.location.pathname.slice(1);
const search = window.location.search.slice(1);

let recUrl = `/recs/${group}`;
if (search.length > 1) {
    recUrl += `?date=${search}`;
}
const recResponse = fetch(recUrl);

const memberUrl = `/members/${group}`;
const memResponse = fetch(memberUrl);

Promise.all([recResponse, memResponse]).then(async ([recsRes, memRes]) => {
    const recs = await recsRes.json();
    const names = await memRes.json();

    const tableElement = document.getElementById('table');

    if (recs.length < 1) {
        tableElement.innerHTML = '今日尚无出刀记录';
        return false;
    }

    const recType = ['完整刀', '尾刀', '余刀', '余尾刀'];

    const bossList = [];
    const uids = Object.keys(names);
    const dataRows = uids.map(uid => [uid, names[uid], 0, 0, 0]);
    const datas = uids.map(_ => []);

    let lastBoss = '';
    let dmgStack = 0;
    recs.forEach(({ boss, dmg, flag, round, score, time, uid }) => {
        const currentBoss = `${round}周目${getBossName(round, boss)}`;
        if (currentBoss != lastBoss) {
            lastBoss = currentBoss;
            dmgStack = 0;
            bossList.push(currentBoss);
        }

        const uidIndex = uids.indexOf(uid);
        datas[uidIndex].push([
            bossList.length - 1,
            dmgStack,
            dmg + dmgStack,
            dmg,
            time.slice(-5),
        ]);
        dmgStack += dmg;

        const row = [...dataRows[uidIndex]];
        row[2] += flag === 0 ? 1 : 0.5;
        row[3] += score;
        row[4] += dmg;
        row.push(
            `(${time.slice(-5)})${currentBoss.slice(-2)}${
                recType[flag]
            } ${toThousands(dmg)}`
        );
        dataRows[uidIndex] = [...row];
    });

    const series = uids.map((uid, uindex) => ({
        name: names[uid],
        type: 'custom',
        data: datas[uindex],
        encode: { x: 0, y: [1, 2], tooltip: [3, 4] },
        renderItem,
    }));
    const options = {
        series,
        legend: {
            data: uids.map(uid => names[uid]),
        },
        grid: {
            left: '2%',
            right: '2%',
            containLabel: true,
        },
        xAxis: [
            {
                type: 'category',
                data: bossList,
            },
        ],
        yAxis: [
            {
                type: 'value',
                axisLabel: { formatter: value => `${value / 10000}w` },
                min: 0,
                max: value => Math.max(value.max, 10000000),
            },
        ],
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
        },
        toolbox: { feature: { saveAsImage: {} } },
    };
    const barChart = echarts.init(document.getElementById('bar'));
    barChart.setOption(options);

    const timeRange = [
        recs[0]['time'].slice(-11),
        recs[recs.length - 1]['time'].slice(-5),
    ];
    const tableHead = `<table class="gridtable"><thead><tr><th></th><th>ID</th>
    <th>昵称</th><th>出刀</th><th>分数</th><th>伤害</th><th>${timeRange.join(
        ' ~ '
    )}</th></tr></thead><tbody>`;
    const tableEnd = '</tbody></table>';
    const tableRows = dataRows
        .sort((a, b) => b[2] * 300000000 + b[3] - a[2] * 300000000 - a[3])
        .map(r => {
            r[0] = dataDesensitization(r[0]);
            r[3] = toThousands(r[3]);
            r[4] = toThousands(r[4]);
            return r;
        })
        .map(
            (r, i) =>
                `<tr><td>${i + 1}</td>${r
                    .map(c => `<td>${c}</td>`)
                    .join('')}</tr>`
        )
        .join('');
    tableElement.innerHTML = tableHead + tableRows + tableEnd;
});
