import { GetStaticPaths, GetStaticProps } from 'next';
import React from 'react';

import AppBar from '../../components/AppBar';
import PersonalChart from '../../components/PersonalChart';
import TablePersonal from '../../components/TablePersonal';
import { Recs } from '../../utils';

type RouteParams = {
    gid: string;
    uid: string;
};

interface PageProps {
    recs: Array<Recs>;
    name: string;
}

const GroupPage: React.FunctionComponent<PageProps> = ({ recs, name }) => {
    if (!recs) {
        return <div>Loading</div>;
    }

    return (
        <>
            <AppBar title={`${name} 出刀信息`} />
            <TablePersonal recs={recs} />
            <PersonalChart recs={recs} />
        </>
    );
};

export const getStaticProps: GetStaticProps<PageProps, RouteParams> = async ({ params }) => {
    if (params) {
        const { gid, uid } = params;

        const recs = await (await fetch(`http://127.0.0.1:8080/recs?g=${gid}&u=${uid}`)).json();
        const name = await (await fetch(`http://127.0.0.1:8080/mem?g=${gid}&u=${uid}`)).text();

        if (recs && name) {
            return {
                props: { name, recs },
                revalidate: 60,
            };
        }
    }

    return {
        props: {
            recs: [],
            name: '',
        },
        revalidate: 1,
    };
};

export const getStaticPaths: GetStaticPaths<RouteParams> = async () => {
    return {
        paths: [],
        fallback: true,
    };
};

export default GroupPage;
