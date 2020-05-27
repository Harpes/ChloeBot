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
function dataDesensitization(num) {
    const numStr = `${num}`;
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

const jsonUrl = 'data/' + window.location.search.slice(1) + '.json';
const request = new XMLHttpRequest();
request.open('get', jsonUrl);
request.send(null);
request.onload = () => {
    if (request.status !== 200) return;
    const records = JSON.parse(request.responseText);
    // { uid, time, round, boss, dmg, user_name, score, type, flag }

    const names = {};
    const uidSet = new Set();
    const categoriesSet = new Set();

    records.forEach(({ uid, round, user_name, type }) => {
        names[uid] = user_name;
        uidSet.add(uid);
        categoriesSet.add(`${round}周目${type.slice(0, 2)}`);
    });

    const category = Array.from(categoriesSet);
    const userIds = Array.from(uidSet);
    const datas = userIds.map(_ => []);
    const rows = userIds.map(uid => [uid, names[uid], 0, 0, 0]);

    let lastBoss = '';
    let dmgStack = 0;
    records.forEach(({ uid, round, dmg, type, score, flag, time }) => {
        const bossName = `${round}周目${type.slice(0, 2)}`;
        if (lastBoss !== bossName) {
            lastBoss = bossName;
            dmgStack = 0;
        }
        datas[userIds.indexOf(uid)].push([
            category.indexOf(bossName),
            dmgStack,
            dmg + dmgStack,
            dmg,
        ]);
        dmgStack += dmg;

        const row = [...rows[userIds.indexOf(uid)]];

        if (flag === 0) row[2] += 1;
        else row[2] += 0.5;

        row[3] += score;
        row[4] += dmg;

        row.push(`(${time.slice(-5)})${type} ${toThousands(dmg)}`);
        rows[userIds.indexOf(uid)] = [...row];
    });

    const series = userIds.map((uid, uindex) => ({
        name: names[uid],
        type: 'custom',
        data: datas[uindex],
        encode: { x: 0, y: [1, 2], tooltip: 3 },
        renderItem,
    }));

    const options = {
        series,
        legend: {
            data: userIds.map(uid => names[uid]),
        },
        grid: {
            left: '2%',
            right: '2%',
            containLabel: true,
        },
        xAxis: [
            {
                type: 'category',
                data: category,
            },
        ],
        yAxis: [
            {
                type: 'value',
                axisLabel: { formatter: value => `${value / 10000}w` },
                min: 0,
                max: value => Math.max(value.max, 15000000),
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
        records[0]['time'].slice(-5),
        records[records.length - 1]['time'].slice(-5),
    ];
    const tableElement = document.getElementById('table');
    const tableHead = `<table class="gridtable"><thead><tr><th></th><th>ID</th>
    <th>昵称</th><th>出刀</th><th>分数</th><th>伤害</th><th>${timeRange.join(
        ' ~ '
    )}</th></tr></thead><tbody>`;
    const tableEnd = '</tbody></table>';
    const tableRows = rows
        .sort((a, b) => b[3] - a[3])
        .map(r => {
            r[0] = dataDesensitization(r[0]);
            r[3] = toThousands(parseInt(r[3]));
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
};
