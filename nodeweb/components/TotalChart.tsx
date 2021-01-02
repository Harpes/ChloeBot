import ReactEchartsCore from 'echarts-for-react/lib/core';
import 'echarts/lib/chart/bar';
import 'echarts/lib/component/legend';
import 'echarts/lib/component/tooltip';
import echarts, { EChartOption } from 'echarts/lib/echarts';
import React from 'react';
import 'zrender/lib/core/util';

import { color, Mems, Recs, shortNumbers } from '../utils';

interface Props {
    recs: Array<Recs>;
    mems: Mems;
}

const names = ['一王', '二王', '三王', '四王', '五王'];

const RankChart: React.FunctionComponent<Props> = ({ recs, mems }) => {
    const uids = Object.keys(mems);
    const dataRows = uids.map((_, i) => [0, 0, 0, 0, 0, 0, i]);

    recs.forEach(({ uid, boss, score }) => {
        const row = dataRows[uids.indexOf(uid)];
        row[0] += score;
        row[boss] += score;
    });
    dataRows.sort((a, b) => b[0] - a[0]);

    const option: EChartOption = {
        legend: {},
        series: names.map((bossName, boss) => {
            return {
                name: bossName,
                type: 'bar',
                stack: 'score',
                color: color[boss],
                data: dataRows.map(row => row[boss + 1]),
            };
        }),
        grid: {
            left: '2%',
            right: '2%',
            containLabel: true,
        },
        xAxis: [
            {
                type: 'category',
                data: dataRows.map(r => mems[uids[r[6]]]),
                axisLabel: {
                    interval: 0,
                    rotate: 90,
                },
            },
        ],
        yAxis: [
            {
                type: 'value',
                axisLabel: {
                    formatter: (value: number) => shortNumbers(value),
                },
                min: 0,
                max: value => Math.max(value.max, 10000000),
            },
        ],
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
        },
    };

    return <ReactEchartsCore style={{ height: 600 }} echarts={echarts} option={option} />;
};

export default RankChart;
