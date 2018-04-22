import React, { Component } from 'react';


const developerKey = 'AIzaSyCir9AWwfpuav6m6UqG5k3kQ3Nv9qoTC6Y';
const clientId = '144187155988-dvcd62a8sripg171p9aensumd1tnancf.apps.googleusercontent.com';
const scope = 'https://www.googleapis.com/auth/drive.readonly';


export default class DropboxChooser extends Component {
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
        let documents = data.docs.map(doc => ({
            doc_id: doc.id,
            mime: doc.mimeType,
            name: doc.name,
            token: this.state.oauthToken,
            type: 'drive',
        }))
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
