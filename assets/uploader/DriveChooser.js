import React, { Component } from 'react';


const developerKey = 'AIzaSyCir9AWwfpuav6m6UqG5k3kQ3Nv9qoTC6Y';
const clientId = '144187155988-dvcd62a8sripg171p9aensumd1tnancf.apps.googleusercontent.com';
const scope = 'https://www.googleapis.com/auth/drive.readonly';

class DriveDocument {
    constructor(file_id, mime, name, token) {
        this.file_id = file_id
        this.mime = mime
        this.name = name
        this.token = token

        this.state = "CREATED"
        this.type = "DRIVE"
    }

    upload(slug) {
        var formData = new FormData()

        formData.append('file_id', this.file_id)
        formData.append('title', this.name)
        formData.append('token', this.token)
        formData.append('course', slug)

        this.tags.map(tag => {
            formData.append('tags', tag)
        })

        upload_form_data(formData, UPLOAD_URL)
    }

}



export default class DriveChooser extends Component {
    onPickerDone = (data) => {
        if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
            this.onPickerSuccess(data)
        } else if (data[google.picker.Response.ACTION] == google.picker.Action.CANCEL) {
            this.onPickerCancel()
        } else if (data[google.picker.Response.ACTION] == google.picker.Action.LOADED) {
            // NOP
        }
    }

    onPickerSuccess = (data) => {
        console.log(data)
        let documents = data.docs.map(doc => (
            new DriveDocument(doc.id, doc.mimeType, doc.name, this.state.oauthToken)
        ))
        console.log("New documents from Google DRIVE", documents)
        this.props.onFiles(documents)
    }

    onPickerCancel = () => {}

    runPicker = () => {
        if(this.state.oauthToken === null){
            gapi.load('auth', {'callback': this.onAuthApiLoad});
        }
        gapi.load('picker', {'callback': this.onPickerApiLoad});
    }

    onAuthApiLoad = () => {
        window.gapi.auth.authorize(
            {
                'client_id': clientId,
                'scope': scope,
            },
            this.onAuthResult
        );
    }

    onAuthResult = (authResult) => {
        if (authResult && !authResult.error) {
            this.setState({oauthToken: authResult.access_token});
            this.createPicker();
        }
    }

    onPickerApiLoad = () => {
        this.setState({pickerApiLoaded: true});
        this.createPicker();
    }


    createPicker = () => {
        if (this.state.pickerApiLoaded && this.state.oauthToken) {
            let view = new google.picker.DocsView()
                .setOwnedByMe(false)

            let picker = new google.picker.PickerBuilder().
                addView(google.picker.ViewId.DOCS).
                addView(google.picker.ViewId.FOLDERS).
                addView(google.picker.ViewId.PDFS).
                addView(view).
                enableFeature(google.picker.Feature.MULTISELECT_ENABLED).
                setOAuthToken(this.state.oauthToken).
                setDeveloperKey(developerKey).
                setCallback(this.onPickerDone).
                build();

            picker.setVisible(true);
        }
    }

    state = {
        oauthToken: null,
        pickerApiLoaded: false,
    }

    render = () => {
        return (<div>
            <button onClick={this.runPicker} className="button success">
                <i className="fi-social-drive"></i>&nbsp;
                Importer depuis Google Drive
            </button>
        </div>)
    }
}
