import Link from '@material-ui/core/Link';
import React from 'react';

import { dataDesensitization, Mems, Recs, shortNumbers, toThousands } from '../utils';
import { cellStyle, headerStyle } from './Table';

interface Props {
    recs: Array<Recs>;
    mems: Omit<Mems, 'name'>;
    gid: string;
    children: JSX.Element;
}

const Table: React.FunctionComponent<Props> = ({ recs, mems, gid, children }) => {
    if (!recs || recs.length < 1) {
        return null;
    }

    const uids = Object.keys(mems);
    const dataRows = uids.map(uid => [uid, mems[uid], 0, 0, 0, 0, 0, 0, 0, 0]) as any[];

    const timeRange = [recs[0].time.slice(-11), recs[recs.length - 1].time.slice(-11)];
    let [totalNums, totalScore, totalDmg] = [0, 0, 0];

    recs.forEach(({ boss, dmg, flag, score, uid }) => {
        totalNums += flag === 0 ? 1 : 0.5;
        totalScore += score;
        totalDmg += dmg;

        const row = dataRows[uids.indexOf(uid)];

        row[2] += flag === 0 ? 1 : 0.5;
        row[3] += score;
        row[4] += dmg;
        row[4 + boss] += score;
    });
    dataRows.sort((a, b) => b[3] - a[3]);

    const td = (value: number | string | JSX.Element, index: number) => (
        <td style={cellStyle} key={`${index}`}>
            {value}
        </td>
    );

    const renderRow = ([uid, name, nums, score, dmg, ...detail]: any, index: number) => {
        return (
            <tr key={uid}>
                {[
                    index + 1,
                    dataDesensitization(uid),
                    <Link href={`${gid}/${uid}`}>{name}</Link>,
                    nums,
                    shortNumbers(score),
                    shortNumbers(dmg),
                    ...detail.map((bossScore: number) =>
                        bossScore === 0 ? '' : `(${((bossScore * 100) / score).toFixed(1)}%) ${toThousands(bossScore)}`
                    ),
                ].map(td)}
            </tr>
        );
    };

    return (
        <table style={{ borderWidth: 1, borderColor: '#666666', borderCollapse: 'collapse', fontSize: 14 }}>
            <thead>
                <tr>
                    <th />
                    <th style={headerStyle}>QQ</th>
                    <th style={headerStyle}>昵称</th>
                    <th style={headerStyle}>出刀</th>
                    <th style={headerStyle}>分数</th>
                    <th style={headerStyle}>伤害</th>
                    <th style={headerStyle} colSpan={2}>
                        {timeRange.join(' ~ ')}
                    </th>
                    <th style={headerStyle} colSpan={3}>
                        {children}
                    </th>
                </tr>
                <tr>
                    <th style={headerStyle} colSpan={3}>
                        总计
                    </th>
                    <th style={headerStyle}>{totalNums}</th>
                    <th style={headerStyle}>{`${shortNumbers(totalScore)}`}</th>
                    <th style={headerStyle}>{`${shortNumbers(totalDmg)}`}</th>
                    <th style={headerStyle}>一王分数</th>
                    <th style={headerStyle}>二王分数</th>
                    <th style={headerStyle}>三王分数</th>
                    <th style={headerStyle}>四王分数</th>
                    <th style={headerStyle}>五王分数</th>
                </tr>
            </thead>
            <tbody>{dataRows.map(renderRow)}</tbody>
        </table>
    );
};

export default Table;
