import type { AppProps } from 'next/app';
import Head from 'next/head';

function MyApp({ Component, pageProps }: AppProps) {
    return (
        <>
            <Head>
                <title>出刀统计</title>
                <meta name="viewport" content="initial-scale=0.5, width=device-width" />
            </Head>
            <Component {...pageProps} />
        </>
    );
}

export default MyApp;
