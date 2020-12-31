import ReactEchartsCore from 'echarts-for-react/lib/core';
import 'echarts/lib/chart/bar';
import 'echarts/lib/chart/custom';
import 'echarts/lib/component/legend';
import 'echarts/lib/component/tooltip';
import echarts, { EChartOption } from 'echarts/lib/echarts';
import React from 'react';
import 'zrender/lib/core/util';

import { getBossDisplayName, Mems, Recs } from '../utils';

interface Props {
    recs: Array<Recs>;
    mems: Omit<Mems, 'name'>;
}

const renderItem: EChartOption.SeriesCustom.RenderItem = (params, api) => {
    const [index, start, end, dmg] = [0, 1, 2, 3].map(i => api.value!(i));
    const x = api.coord!([index, start])[0];
    const y = api.coord!([index, end])[1];
    const [width, height] = api.size!([1, -dmg]);

    const rectShape = echarts.graphic.clipRectByRect(
        {
            x: x - width * 0.3,
            y,
            width: width * 0.6,
            height,
        },
        {
            x: (params as any).coordSys.x,
            y: (params as any).coordSys.y,
            width: (params as any).coordSys.width,
            height: (params as any).coordSys.height,
        }
    );

    return (
        rectShape && {
            type: 'rect',
            shape: rectShape,
            style: api.style!(),
        }
    );
};

const ProcessChart: React.FunctionComponent<Props> = ({ recs, mems }) => {
    const bossList: Array<string> = [];
    const uids = Object.keys(mems);
    const datas: Array<Array<[number, number, number, number, string]>> = uids.map(_ => []);

    let lastBoss = '',
        dmgStack = 0;

    recs.forEach(({ boss, dmg, round, time, uid }) => {
        const currentBoss = `${round}周目${getBossDisplayName(round, boss)}`;
        if (currentBoss !== lastBoss) {
            lastBoss = currentBoss;
            dmgStack = 0;
            bossList.push(currentBoss);
        }

        datas[uids.indexOf(uid)].push([bossList.length - 1, dmgStack, dmg + dmgStack, dmg, time.slice(-5)]);
        dmgStack += dmg;
    });

    const option: EChartOption = {
        legend: {},
        series: uids.map((uid, uindex) => ({
            name: mems[uid],
            type: 'custom',
            data: datas[uindex],
            encode: { x: 0, y: [1, 2], tooltip: [3, 4] },
            renderItem,
        })),
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
                axisLabel: {
                    formatter: (value: number) => `${value / 10000}w`,
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

export default ProcessChart;
