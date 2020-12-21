import moment from 'moment';

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
    const date = moment()
        .year(dateValue.year())
        .month(dateValue.month())
        .date(dateValue.date())
        .hour(4);

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

export const dataDesensitization = (uidStr: string) => {
    const numStr = atob(uidStr);
    const len = numStr.length;
    if (len > 4) {
        return numStr.substring(0, 2) + '*' + numStr.substring(len - 3, len);
    }
    return numStr;
};
