import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import React from 'react';

interface Props {
    value: string;
    setValue: (value: string) => void;
    children: JSX.Element[];
}

const NativeSelects: React.FunctionComponent<Props> = ({ value, setValue, children }) => {
    const handleChange = (event: any) => {
        const newValue = event.target.value;
        setValue(newValue);
    };

    return (
        <FormControl style={{ minWidth: 120, maxHeight: 24 }}>
            <Select native value={value} onChange={handleChange}>
                {children}
            </Select>
        </FormControl>
    );
};

export default NativeSelects;
