import React, { Component } from 'react';

import DropboxChooser from './DropboxChooser';
import DriveChooser from './DriveChooser';


export default class Uploader extends Component {
    render() {
        return (<div>
            <DropboxChooser />
            <DriveChooser />
        </div>);
    }
}
