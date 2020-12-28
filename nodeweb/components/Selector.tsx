import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import { createStyles, Theme, withStyles, WithStyles } from '@material-ui/core/styles';
import React from 'react';

const styles = (theme: Theme) =>
    createStyles({
        formControl: {
            minWidth: 120,
            maxHeight: theme.spacing(2),
        },
    });

interface Props extends WithStyles<typeof styles> {
    options: Array<{ value: string; title: string }>;
    value: string;
    setValue: (value: string) => void;
}

const NativeSelects: React.FunctionComponent<Props> = ({ classes, options, value, setValue }) => {
    const handleChange = (event: any) => {
        const newValue = event.target.value;
        setValue(newValue);
    };

    return (
        <FormControl className={classes.formControl}>
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

export default withStyles(styles)(NativeSelects);
