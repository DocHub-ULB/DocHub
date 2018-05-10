import React, { Component } from 'react';
import Dropzone from 'react-dropzone'

const UPLOAD_URL = '/api/documents/upload'

class DndDocument {

    constructor(fileobj, name) {
        this.fileobj = fileobj
        this.name = name
        this.extension = name.split('.').pop()

        this.state = "CREATED"
        this.type = "DND"
    }

    upload(slug) {
        var formData = new FormData()

        formData.append('title', this.name)
        formData.append('file', this.fileobj, this.name + '.' + this.extension)
        formData.append('course', slug)

        this.tags.map(tag => {
            formData.append('tags', tag)
        })

        upload_form_data(formData, UPLOAD_URL)
    }
}

export default class Drop extends Component {

    onDrop = (acceptedFiles, rejectedFiles) => {
        let documents = acceptedFiles.map(file => (
            new DndDocument(file, file.name)
        ))
        this.props.onFiles(documents)
    }

    render = () => {
        return (<div>
            <Dropzone onDrop={this.onDrop} className="dropzone" activeClassName="activedrop" rejectClassName="rejectdrop"/>
        </div>)
    }
}
