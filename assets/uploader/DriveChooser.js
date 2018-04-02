import React, { Component } from 'react';


const scope = 'https://www.googleapis.com/auth/drive.readonly';


export default class DropboxChooser extends Component {
    onPickerDone = (data) => {
        console.log("Picker done")
        if (data[google.picker.Response.ACTION] == google.picker.Action.PICKED) {
            this.onPickerSuccess(data)
        } else {
            this.onPickerCancel()
        }
    }

    onPickerSuccess = (data) => {
        console.log(this.state.oauthToken)
        console.log(data)
    }

    onPickerCancel = () => {
        console.log("Cancel")
    }

    runPicker = () => {
        gapi.load('auth', {'callback': this.onAuthApiLoad});
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
            var picker = new google.picker.PickerBuilder().
                addView(google.picker.ViewId.DOCS).
                addView(google.picker.ViewId.DOCUMENTS).
                addView(google.picker.ViewId.FOLDERS).
                addView(google.picker.ViewId.PDFS).
                // .enableFeature(google.picker.Feature.NAV_HIDDEN).
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
        return <button onClick={this.runPicker}>Google Drive</button>
    }
}
