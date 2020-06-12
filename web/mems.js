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
function pad(num, n = 2) {
    let len = num.toString().length;
    while (len < n) {
        num = '0' + num;
        len++;
    }
    return num;
}
function getDay(value) {
    const [year, month, date, hour, min] = value
        .replace(/\//g, ':')
        .replace(' ', ':')
        .split(':');
    const datetime = new Date(
        year,
        parseInt(month) - 1,
        date,
        parseInt(hour) - 5,
        min
    );

    return `${pad(datetime.getMonth() + 1)}/${pad(datetime.getDate())}`;
}

const [group, user] = window.location.pathname.slice(1).split('/');
fetch(`/recs/${group}?uid=${user}`)
    .then(res => res.json())
    .then(recs => {
        const recType = ['完整刀', '尾刀', '余刀', '余尾刀'];

        const dataRows = [];
        const bossScores = [[], [], [], [], []];
        const bossDmgs = [[], [], [], [], []];

        let lastDate = '';
        recs.forEach(({ boss, dmg, flag, round, score, time }) => {
            const currentDate = getDay(time);
            if (lastDate != currentDate) {
                lastDate = currentDate;
                dataRows.push([currentDate, 0, 0]);
            }

            const rowIndex = dataRows.length - 1;

            if (!bossScores[boss - 1][rowIndex]) {
                bossScores[boss - 1][rowIndex] = 0;
                bossDmgs[boss - 1][rowIndex] = 0;
            }
            bossScores[boss - 1][rowIndex] += score;
            bossDmgs[boss - 1][rowIndex] += dmg;

            const row = [...dataRows[rowIndex]];
            row[1] += score;
            row[2] += dmg;
            row.push(
                `${getBossName(round, boss)}${recType[flag]}\n${toThousands(
                    dmg
                )}`
            );
            if (flag === 0) row.push('');
            dataRows[rowIndex] = [...row];
        });

        const color = ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae'];
        const bossNames = ['一王', '二王', '三王', '四王', '五王'];
        const series = [].concat(
            bossDmgs.map((data, boss) => ({
                name: bossNames[boss] + '伤害',
                type: 'bar',
                stack: 'dmg',
                barMaxWidth: '20%',
                data,
            })),
            bossScores.map((data, boss) => ({
                name: bossNames[boss],
                type: 'bar',
                stack: 'score',
                barMaxWidth: '20%',
                data,
            }))
        );
        const options = {
            series,
            legend: {},
            color,
            grid: {
                left: '2%',
                right: '2%',
                containLabel: true,
            },
            xAxis: [
                {
                    type: 'category',
                    data: dataRows.map(([d]) => d),
                },
            ],
            yAxis: [
                {
                    type: 'value',
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
        const tableHead = `<table class="gridtable"><thead><tr>
            <th>日期</th><th>分数</th><th>伤害</th>
            <th colspan="2">1</th><th colspan="2">2</th><th colspan="2">3</th></tr></thead><tbody>`;
        const tableEnd = '</tbody></table>';
        const tableRows = dataRows
            .map(r => {
                r[1] = toThousands(r[1]);
                r[2] = toThousands(r[2]);
                return r;
            })
            .map(r => `<tr>${r.map(c => `<td>${c}</td>`).join('')}</tr>`)
            .join('');
        tableElement.innerHTML = tableHead + tableRows + tableEnd;
    });
