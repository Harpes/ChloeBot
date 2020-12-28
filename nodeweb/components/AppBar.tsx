import AppBar from '@material-ui/core/AppBar';
import { createStyles, Theme, WithStyles, withStyles } from '@material-ui/core/styles';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import React from 'react';

const styles = (theme: Theme) =>
    createStyles({
        root: {
            flexGrow: 1,
            margin: -8,
            marginBottom: theme.spacing(1),
        },
    });

interface Props extends WithStyles<typeof styles> {
    title: string;
}

const DenseAppBar: React.FunctionComponent<Props> = ({ classes, title }) => {
    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Toolbar variant="dense">
                    <Typography color="inherit">{title}</Typography>
                </Toolbar>
            </AppBar>
        </div>
    );
};

export default withStyles(styles)(DenseAppBar);
