import Link from '@material-ui/core/Link';
import React from 'react';

import { dataDesensitization, getBossDisplayName, Mems, Recs, recType, shortNumbers, toThousands } from '../utils';

export const headerStyle: React.CSSProperties = {
    borderWidth: 1,
    borderStyle: 'solid',
    borderColor: '#666666',
    backgroundColor: '#DEDEDE',
    textAlign: 'center',
};

export const cellStyle: React.CSSProperties = {
    padding: 2,
    borderWidth: 1,
    borderStyle: 'solid',
    borderColor: '#666666',
    backgroundColor: '#FFFFFF',
    textAlign: 'right',
};

interface Props {
    recs: Array<Recs>;
    mems: Omit<Mems, 'name'>;
    gid: string;
    children?: JSX.Element;
}

const Table: React.FunctionComponent<Props> = ({ recs, mems, gid, children }) => {
    if (!recs || recs.length < 1) {
        return null;
    }

    const uids = Object.keys(mems);
    const dataRows = uids.map(uid => [uid, mems[uid], 0, 0, 0]) as any[];

    const timeRange = [recs[0].time.slice(-11), recs[recs.length - 1].time.slice(-11)];
    let [wholeNum, halfNum] = [0, 0];
    let [totalScore, totalDmg] = [0, 0];

    recs.forEach(({ boss, dmg, flag, score, round, time, uid }) => {
        totalScore += score;
        totalDmg += dmg;

        const uidIndex = uids.indexOf(uid);
        const row = dataRows[uidIndex];

        row[3] += score;
        row[4] += dmg;

        row.push(`(${time.slice(-5)})${getBossDisplayName(round, boss)}${recType(flag)} ${toThousands(dmg)}`);

        if (flag === 0) {
            row.push('');
            row[2] += 1;
            wholeNum += 1;
        } else {
            row[2] += 0.5;
            wholeNum += flag === 1 ? 0 : 1;
            halfNum += flag === 1 ? 1 : -1;
        }
    });
    dataRows.sort((a, b) => b[2] * 300000000 + b[3] - a[2] * 300000000 - a[3]);

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
                    ...detail,
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
                    <th style={headerStyle} colSpan={2}>{`完整刀：${wholeNum}，尾刀：${halfNum}。`}</th>
                    {children ? (
                        <th style={headerStyle} colSpan={2}>
                            {children}
                        </th>
                    ) : null}
                </tr>
            </thead>
            <tbody>
                {dataRows.map(renderRow)}
                <tr>
                    <td style={headerStyle} colSpan={4}>
                        总计
                    </td>
                    <td style={headerStyle}>{`${shortNumbers(totalScore)}`}</td>
                    <td style={headerStyle}>{`${shortNumbers(totalDmg)}`}</td>
                </tr>
            </tbody>
        </table>
    );
};

export default Table;
