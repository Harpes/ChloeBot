import moment from 'moment';

export const color = ['#c23531', '#2f4554', '#61a0a8', '#d48265', '#91c7ae'];

const recTypeList = ['整刀', '尾刀', '余刀', '余尾刀'];
export const recType = (flag: number) => recTypeList[flag];

export type Recs = {
    boss: number;
    dmg: number;
    flag: number;
    round: number;
    score: number;
    time: string;
    uid: string;
};

export type Mems = {
    name: string;
    [index: string]: string;
};

export const getDayOfDateString = (value: string) => {
    const dateValue = moment(value, 'YYYY/MM/DD HH:mm');
    const date = moment().year(dateValue.year()).month(dateValue.month()).date(dateValue.date()).hour(4);

    if (dateValue.isBefore(date)) date.subtract(1, 'day');

    return date.format('YYYY/MM/DD');
};

export const getBossDisplayName = (rou: number, boss: number) => {
    const stage = rou > 34 ? 'D' : rou > 10 ? 'C' : rou > 3 ? 'B' : 'A';
    return `${stage}${boss}`;
};

export const toThousands = (value: number) => {
    let num = (value || 0).toString();
    let result = '';

    while (num.length > 3) {
        result = ',' + num.slice(-3) + result;
        num = num.slice(0, num.length - 3);
    }
    if (num) {
        result = num + result;
    }
    return result;
};

export const dataDesensitization = (sourceStr: string) => {
    const numStr = Buffer.from(sourceStr, 'base64').toString();
    const len = numStr.length;
    if (len > 4) {
        return numStr.substring(0, 2) + '*' + numStr.substring(len - 3, len);
    }
    return numStr;
};

export const shortNumbers = (value: number) => {
    if (value > 100000000) {
        return `${(value / 100000000).toFixed(3)}e`;
    } else if (value > 10000) {
        return `${(value / 10000).toFixed(0)}w`;
    } else if (value > 1000) {
        return `${(value / 1000).toFixed(2)}k`;
    }

    return `${value}`;
};
