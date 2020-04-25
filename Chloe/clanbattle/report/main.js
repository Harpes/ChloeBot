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
    const nullValues = new Array(category.length).fill(null);
    const userIds = Array.from(uidSet);
    const datas = userIds.map(_ => [...nullValues]);
    const rows = userIds.map(uid => [uid, names[uid], 0, 0]);

    records.forEach(({ uid, round, dmg, type, score, flag, time }) => {
        datas[userIds.indexOf(uid)][
            category.indexOf(`${round}周目${type.slice(0, 2)}`)
        ] += dmg;

        const row = [...rows[userIds.indexOf(uid)]];
        // if (flag !== 1) row[2] += 1;
        if (flag === 0) row[2] += 1;
        else row[2] += 0.5;
        row[3] += score;
        row.push(`(${time.slice(-5)})${type} ${toThousands(dmg)}`);
        rows[userIds.indexOf(uid)] = [...row];
    });

    const series = userIds.map((uid, uindex) => ({
        name: names[uid],
        type: 'bar',
        stack: 'dmg',
        data: datas[uindex],
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
                minInterval: 2000000,
                axisLabel: { formatter: value => `${value / 10000}w` },
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

    const tableElement = document.getElementById('table');
    const tableHead =
        '<table class="gridtable"><thead><tr><th></th><th></th><th>昵称</th><th>出刀</th><th>分数</th></tr></thead><tbody>';
    const tableEnd = '</tbody></table>';
    const tableRows = rows
        .sort((a, b) => b[3] - a[3])
        .map(r => {
            r[3] = toThousands(parseInt(r[3]));
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
