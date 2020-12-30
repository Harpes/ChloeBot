import { GetServerSideProps } from 'next';
import React, { useCallback, useState } from 'react';

import AppBar from '../../components/AppBar';
import TotalChart from '../../components/TotalChart';
import ProcessChart from '../../components/ProcessChart';
import Selector from '../../components/Selector';
import Table from '../../components/Table';
import TableTotal from '../../components/TableTotal';
import { getDayOfDateString, Mems, Recs } from '../../utils';

type RouteParams = {
    gid: string;
};

interface PageProps extends RouteParams {
    recs: Array<Recs>;
    mems: Mems;
}

const GroupPage: React.FunctionComponent<PageProps> = ({ recs, mems, gid }) => {
    const groupName = mems.name || '';
    delete (mems as any).name;
    const recsMap: { [index: string]: PageProps['recs'] } = {};

    const dateSet: Set<string> = new Set<string>();
    recs.forEach(rec => {
        const { time } = rec;

        const date = getDayOfDateString(time);
        dateSet.add(date);

        if (!recsMap[date]) recsMap[date] = [];
        recsMap[date].push(rec);
    });
    const newDateList = Array.from(dateSet).sort();

    if (!recs || recs.length < 1) {
        return <div>找不到记录</div>;
    }

    const [dateList, setDateList] = useState(newDateList);
    const [currentDate, setCurrentDate] = useState(newDateList[newDateList.length - 1]);
    const [showAll, setShowAll] = useState(false);

    const setOption = useCallback((optionValue: string) => {
        if (optionValue === 'all') {
            setShowAll(true);
        } else {
            setCurrentDate(optionValue);
            setShowAll(false);
        }
    }, []);

    if (dateList.length !== newDateList.length) {
        setDateList(newDateList);
        setCurrentDate(newDateList[newDateList.length - 1]);
    }

    if (dateSet.size < 1) {
        return null;
    }

    const options = [
        <option key="all" value="all">
            全部
        </option>,
        ...dateList.map(value => (
            <option key={value} value={value}>
                {value}
            </option>
        )),
    ];

    return (
        <>
            <AppBar title={`公会 ${groupName}`} />
            {showAll ? (
                <>
                    <TableTotal mems={mems} recs={recs} gid={gid}>
                        <Selector value="all" setValue={setOption}>
                            {options}
                        </Selector>
                    </TableTotal>
                    <TotalChart mems={mems} recs={recs} />
                </>
            ) : (
                <>
                    <Table mems={mems} recs={recsMap[currentDate]} gid={gid}>
                        <Selector value={currentDate} setValue={setOption}>
                            {options}
                        </Selector>
                    </Table>
                    <ProcessChart mems={mems} recs={recsMap[currentDate]} />
                </>
            )}
        </>
    );
};

export const getServerSideProps: GetServerSideProps<PageProps, RouteParams> = async ({ params }) => {
    if (params) {
        const { gid } = params;

        const recs = await (await fetch('http://127.0.0.1:8080/recs?g=' + gid)).json();
        const mems = await (await fetch('http://127.0.0.1:8080/mems?g=' + gid)).json();

        if (recs && mems) {
            return {
                props: { mems, recs, gid },
            };
        }
    }

    return {
        props: {
            recs: [],
            mems: { name: '' },
            gid: '',
        },
    };
};

export default GroupPage;
