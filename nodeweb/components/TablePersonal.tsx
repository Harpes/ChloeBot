import React from 'react';

import { getBossDisplayName, getDayOfDateString, Recs, recType, shortNumbers, toThousands } from '../utils';
import { cellStyle, headerStyle } from './Table';

interface Props {
    recs: Array<Recs>;
}

const Table: React.FunctionComponent<Props> = ({ recs }) => {
    const dataRows: any[] = [];
    const totals: any[] = ['总计', 0, 0, 0];

    let currentDate = '';
    recs.forEach(({ boss, dmg, flag, score, round, time }) => {
        const date = getDayOfDateString(time);
        if (date !== currentDate) {
            currentDate = date;
            dataRows.push([currentDate, 0, 0, 0]);
        }

        const row = dataRows[dataRows.length - 1];
        row[2] += score;
        totals[2] += score;
        row[3] += dmg;
        totals[3] += dmg;
        row.push(`(${time.slice(-5)})${getBossDisplayName(round, boss)}${recType(flag)} ${toThousands(dmg)}`);

        if (flag === 0) {
            row.push('');
            row[1] += 1;
            totals[1] += 1;
        } else {
            row[1] += 0.5;
            totals[1] += 0.5;
        }
    });

    const td = (value: number | string, index: number) => (
        <td key={`${index}`} style={cellStyle}>
            {value}
        </td>
    );

    const renderRow = ([date, nums, score, dmg, ...details]: Array<any>, index: number) => {
        return <tr key={`${index}`}>{[date, nums, toThousands(score), toThousands(dmg), ...details].map(td)}</tr>;
    };

    return (
        <table style={{ borderWidth: 1, borderColor: '#666666', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
                <tr>
                    <th style={headerStyle}>日期</th>
                    <th style={headerStyle}>出刀</th>
                    <th style={headerStyle}>分数</th>
                    <th style={headerStyle}>伤害</th>
                    <th colSpan={2} style={headerStyle}>
                        1
                    </th>
                    <th colSpan={2} style={headerStyle}>
                        2
                    </th>
                    <th colSpan={2} style={headerStyle}>
                        3
                    </th>
                </tr>
            </thead>
            <tbody>
                {dataRows.map(renderRow)}
                <tr>
                    {totals.map((cv, index) => (
                        <td style={headerStyle} key={`${index}`}>
                            {index > 1 ? shortNumbers(cv) : cv}
                        </td>
                    ))}
                </tr>
            </tbody>
        </table>
    );
};

export default Table;
