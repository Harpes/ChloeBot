import Image from 'next/image';
import React from 'react';

const HomePage = () => {
    return <Image src="/chloe.gif" width={500} height={500} alt="chloe" quality={100}></Image>;
};

export default HomePage;
