import ReactEchartsCore from 'echarts-for-react/lib/core';
import 'echarts/lib/chart/bar';
import 'echarts/lib/component/tooltip';
import echarts, { EChartOption } from 'echarts/lib/echarts';
import React from 'react';

import { getDayOfDateString, Recs } from '../utils';

interface Props {
    recs: Array<Recs>;
}

const color = ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae'];
const names = ['一王', '二王', '三王', '四王', '五王'];

const PieChart: React.FunctionComponent<Props> = ({ recs }) => {
    const bossScores: Array<Array<number>> = [[], [], [], [], []];
    const bossDmages: Array<Array<number>> = [[], [], [], [], []];
    const dateList: Array<string> = [];

    let currentDate = '';
    recs.forEach(({ boss, score, time }) => {
        const date = getDayOfDateString(time);
        if (date !== currentDate) {
            currentDate = date;
            dateList.push(currentDate);
        }

        const rowIndex = dateList.length - 1;
        if (!bossScores[boss - 1][rowIndex]) {
            bossScores[boss - 1][rowIndex] = 0;
            bossDmages[boss - 1][rowIndex] = 0;
        }
        bossScores[boss - 1][rowIndex] += score;
        bossDmages[boss - 1][rowIndex] += score;
    });

    const option: EChartOption<EChartOption.SeriesBar> = {
        series: [
            ...bossDmages.map((data, boss) => ({
                name: `${names[boss]}伤害`,
                type: 'bar' as 'bar',
                stack: 'dmg',
                barMaxWidth: '20%',
                data,
            })),
            ...bossScores.map((data, boss) => ({
                name: `${names[boss]}伤害`,
                type: 'bar' as 'bar',
                stack: 'score',
                barMaxWidth: '20%',
                data,
            })),
        ],
        grid: {
            left: '2%',
            right: '2%',
            top: '2%',
            bottom: '2%',
            containLabel: true,
        },
        color,
        xAxis: [
            {
                type: 'category',
                data: dateList,
            },
        ],
        yAxis: [
            {
                type: 'value',
                axisLabel: { formatter: (value: any) => `${value / 10000}w` },
            },
        ],
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'shadow' },
        },
    };

    return <ReactEchartsCore style={{ height: 600 }} echarts={echarts} option={option} />;
};

export default PieChart;
