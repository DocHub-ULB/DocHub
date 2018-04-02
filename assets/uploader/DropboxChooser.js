import React, { Component } from 'react';

const CHOOSER_OPTIONS = {
    // success: function(files) {
    //     alert("Here's the file link: " + files[0].link)
    // },
    // cancel: function() {
    //
    // },

    linkType: "direct",
    multiselect: true,
    extensions: ['.pdf', '.doc', '.docx', 'images', 'documents', 'text'],
    folderselect: false,
};


export default class DropboxChooser extends Component {
    on_success = (files) => {
        let documents = files.map(doc => ({
            doc_id: doc.id,
            name: doc.name,
            type: 'dropbox',
        }))
        console.log("New documents from Dropbox", documents)
        this.props.onFiles(documents)
    }

    on_cancel = () => {
        console.log("Cancel")
    }

    run_chooser = () => {
        var options = {...CHOOSER_OPTIONS, success: this.on_success, cancel: this.on_cancel}
        Dropbox.choose(options);
    }

    render = () => {
        return (<div>
            <button onClick={this.run_chooser} className="button success">
                <i className="fi-social-dropbox"></i>&nbsp;
                Importer depuis Dropbox
            </button>
        </div>)
    }
}
