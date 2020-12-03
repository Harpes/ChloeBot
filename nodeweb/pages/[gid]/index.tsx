import { GetStaticPaths, GetStaticProps } from 'next';
import React from 'react';
import ReactEchartsCore from 'echarts-for-react/lib/core';
import echarts, { EChartOption } from 'echarts/lib/echarts';

import AppBar from '../../components/AppBar';

type Params = {
    gid: string;
};

interface Props extends Params {
    // gid: string;
}

const GroupPage: React.FunctionComponent<Props> = ({ gid }) => {
    return (
        <>
            <AppBar title={gid} />
            <section>
                <ReactEchartsCore
                    echarts={echarts}
                    option={{}}
                    // opts={}
                />
            </section>
        </>
    );
};

export const getStaticProps: GetStaticProps<Props, Params> = async ({
    params,
}) => {
    if (!params || params.gid === '-')
        return {
            props: { gid: '-' },
        };

    return {
        props: { ...params },
        revalidate: 180,
    };
};

export const getStaticPaths: GetStaticPaths<Params> = async () => {
    return {
        paths: [
            {
                params: { gid: '-' },
            },
        ],
        fallback: 'blocking',
    };
};

export default GroupPage;
