import { GetServerSideProps } from 'next';
import React from 'react';

import AppBar from '../../components/AppBar';
import PercentChart from '../../components/PercentChart';
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
    if (!recs) return null;

    return (
        <>
            <AppBar title={`${name} 出刀信息`} />
            <TablePersonal recs={recs} />
            <PercentChart recs={recs} />
        </>
    );
};

export const getServerSideProps: GetServerSideProps<PageProps, RouteParams> = async ({ params }) => {
    if (params) {
        const { gid, uid } = params;

        const recs = await (await fetch(`http://127.0.0.1:8080/recs?g=${gid}&u=${uid}`)).json();
        const name = await (await fetch(`http://127.0.0.1:8080/mem?g=${gid}&u=${uid}`)).text();

        if (recs && name) {
            return {
                props: { name, recs },
            };
        }
    }

    return {
        props: {
            recs: [],
            name: '',
        },
    };
};

export default GroupPage;
