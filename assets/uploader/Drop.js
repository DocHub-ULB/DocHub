import React, { Component } from 'react';
import Dropzone from 'react-dropzone'


export default class Drop extends Component {

    onDrop = (acceptedFiles, rejectedFiles) => {
        let documents = acceptedFiles.map(file => ({
            fileobj: file,
            name: file.name,
            type: 'dnd',
        }))
        this.props.onFiles(documents)
    }

    render = () => {
        return (<div>
            <Dropzone onDrop={this.onDrop} className="dropzone" activeClassName="activedrop" rejectClassName="rejectdrop"/>
        </div>)
    }
}
