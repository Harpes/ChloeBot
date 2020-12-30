import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import React from 'react';

interface Props {
    options: Array<{ value: string; title: string }>;
    value: string;
    setValue: (value: string) => void;
}

const NativeSelects: React.FunctionComponent<Props> = ({ options, value, setValue }) => {
    const handleChange = (event: any) => {
        const newValue = event.target.value;
        setValue(newValue);
    };

    return (
        <FormControl style={{ minWidth: 120, maxHeight: 24 }}>
            <Select native value={value} onChange={handleChange}>
                {options.map(({ value, title }) => (
                    <option key={value} value={value}>
                        {title}
                    </option>
                ))}
            </Select>
        </FormControl>
    );
};

export default NativeSelects;
