import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import React from 'react';

interface Props {
    title: string;
}

const DenseAppBar: React.FunctionComponent<Props> = ({ title }) => {
    return (
        <div style={{ flexGrow: 1, margin: -8, marginBottom: 4 }}>
            <AppBar position="static">
                <Toolbar variant="dense">
                    <Typography color="inherit">{title}</Typography>
                </Toolbar>
            </AppBar>
        </div>
    );
};

export default DenseAppBar;
