import { createStyles, Theme, WithStyles, withStyles } from '@material-ui/core/styles';
import React from 'react';

import { getBossDisplayName, getDayOfDateString, Recs, recType, toThousands } from '../utils';

const styles = (_: Theme) =>
    createStyles({
        root: {
            borderWidth: 1,
            borderColor: '#666666',
            borderCollapse: 'collapse',
            fontSize: 14,
        },
        header: {
            padding: 2,
            borderWidth: 1,
            borderStyle: 'solid',
            borderColor: '#666666',
            backgroundColor: '#DEDEDE',
        },
        cell: {
            padding: 2,
            borderWidth: 1,
            borderStyle: 'solid',
            borderColor: '#666666',
            backgroundColor: '#FFFFFF',
            textAlign: 'right',
        },
    });

interface Props extends WithStyles<typeof styles> {
    recs: Array<Recs>;
}

const Table: React.FunctionComponent<Props> = ({ classes, recs }) => {
    const dataRows: Array<any> = [];
    const totals = [0, 0, 0];

    let currentDate = '';
    recs.forEach(({ boss, dmg, flag, score, round, time }) => {
        const date = getDayOfDateString(time);
        if (date !== currentDate) {
            currentDate = date;
            dataRows.push([currentDate, 0, 0, 0]);
        }

        const row = dataRows[dataRows.length - 1];
        row[2] += score;
        totals[1] += score;
        row[3] += dmg;
        totals[2] += dmg;
        row.push(`(${time.slice(-5)})${getBossDisplayName(round, boss)}${recType(flag)} ${toThousands(dmg)}`);

        if (flag === 0) {
            row.push('');
            row[1] += 1;
            totals[0] += 1;
        } else {
            row[1] += 0.5;
            totals[0] += 0.5;
        }
    });
    dataRows.push(['总计', ...totals] as any);

    const td = (value: number | string, index: number) => (
        <td key={`${index}`} className={classes.cell}>
            {value}
        </td>
    );

    const renderRow = ([date, nums, score, dmg, ...details]: Array<any>, index: number) => {
        return <tr key={`${index}`}>{[date, nums, toThousands(score), toThousands(dmg), ...details].map(td)}</tr>;
    };

    return (
        <table className={classes.root}>
            <thead>
                <tr>
                    <th className={classes.header}>日期</th>
                    <th className={classes.header}>出刀</th>
                    <th className={classes.header}>分数</th>
                    <th className={classes.header}>伤害</th>
                    <th colSpan={2} className={classes.header}>
                        1
                    </th>
                    <th colSpan={2} className={classes.header}>
                        2
                    </th>
                    <th colSpan={2} className={classes.header}>
                        3
                    </th>
                </tr>
            </thead>
            <tbody>{dataRows.map(renderRow)}</tbody>
        </table>
    );
};

export default withStyles(styles)(Table);
