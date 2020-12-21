import { GetServerSideProps } from 'next';
import React from 'react';

import { AppBar, ProcessChart } from '../../components';
import { getDayOfDateString, Mems, Recs } from '../../utils';

type RouteParams = {
    gid: string;
};

interface PageProps {
    recs: Array<Recs>;
    mems: Mems;
}

const date = '2020/11/26';
const timeDemo = '2020/11/26 06:32';

const GroupPage: React.FunctionComponent<PageProps> = ({ recs, mems }) => {
    const dateMap: { [index: string]: PageProps['recs'] } = {};
    const dateSet: Set<string> = new Set<string>();
    recs.forEach(rec => {
        const { time } = rec;

        const date = getDayOfDateString(time);
        dateSet.add(date);

        if (!dateMap[date]) dateMap[date] = [];
        dateMap[date].push(rec);
    });
    const dateList = Array.from(dateSet).sort();

    return (
        <>
            <AppBar title={mems.name + ' 出刀记录'} />
            <section style={{ height: 600 }}>
                <ProcessChart mems={mems} recs={dateMap[date]} />
            </section>
        </>
    );
};

export const getServerSideProps: GetServerSideProps<
    PageProps,
    RouteParams
> = async ({ params }) => {
    if (params) {
        const { gid } = params;

        const recs = await (
            await fetch('http://127.0.0.1:8080/recs?g=' + gid)
        ).json();
        const mems = await (
            await fetch('http://127.0.0.1:8080/mems?g=' + gid)
        ).json();

        if (recs && mems) {
            return {
                props: { mems, recs },
            };
        }
    }

    return {
        props: {
            recs: [],
            mems: { name: '' },
        },
    };
};

export default GroupPage;
