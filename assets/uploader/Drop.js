import React, { Component } from 'react';
import Dropzone from 'react-dropzone'


class DropboxDocument {

    constructor(fileobj, name) {
        this.fileobj = fileobj
        this.name = name

        this.state = "CREATED"
        this.type = "DND"
    }
    
}

export default class Drop extends Component {

    onDrop = (acceptedFiles, rejectedFiles) => {
        let documents = acceptedFiles.map(file => (
            new DropboxDocument(file, file.name)
        ))
        this.props.onFiles(documents)
    }

    render = () => {
        return (<div>
            <Dropzone onDrop={this.onDrop} className="dropzone" activeClassName="activedrop" rejectClassName="rejectdrop"/>
        </div>)
    }
}
