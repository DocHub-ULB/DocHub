import React, { Component } from 'react';

import DropboxChooser from './DropboxChooser';
import DriveChooser from './DriveChooser';
import Drop from './Drop';
import {detect_tags, clean_filename} from './utils'

const type_icons = {
    'dropbox': 'fi-social-dropbox',
    'drive': 'fi-social-drive',
    'dnd': 'fi-monitor',
}

class Tag extends React.Component {
    render = function(){
        let style = {
            border: 'solid 2px ' + this.props.color,
            backgroundColor: this.props.color,
            color: "white",
        };
        let klass = "radius label tag-item";

        return (<span>
            <span onClick={this.clicked}
                        style={style} className={klass}>
            {this.props.name}
            </span>&nbsp;
        </span>);
    }
}

class UploadedFile extends Component {
    source_icon = () => {
        return type_icons[this.props.type]
    }
    render = () => {
        return (<tr>
            <td><i className={this.source_icon()}></i></td>
            <td>{this.props.name} <i className="fi-pencil"></i></td>
            <td>
                {this.props.tags.map(tag => {
                        let instance = this.props.all_tags.find(x => x.name == tag)
                        return <Tag {...instance} />
                })}
                <span className="radius label tag-item" style={{backgroundColor: "grey"}}><i className="fi-plus"></i></span>
            </td>
            <td><i className="fi-x"></i></td>
        </tr>)
    }
}


export default class Uploader extends Component {
    state = {
        files: []
    }

    onFiles = (files) => {
        let processed = files.map(file => {
            file.name = clean_filename(file.name)
            file.tags = detect_tags(file.name)
            return file
        })
        this.setState({files: this.state.files.concat(processed)})
    }

    render() {
        return (
            <div>
                <div className="row">
                    <h1>{this.props.slug} : Upload</h1>
                </div>
                <div className="row">
                    <div className="large-8 columns">
                        <table>
                            <thead>
                                <tr>
                                    <th></th>
                                    <th>Fichier</th>
                                    <th>Tags</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {this.state.files.map(file => <UploadedFile {...file} all_tags={this.props.tags}/>)}
                            </tbody>
                        </table>
                    </div>
                    <div className="large-4 columns">
                        <DropboxChooser onFiles={this.onFiles} />
                        <DriveChooser onFiles={this.onFiles} />
                        <Drop onFiles={this.onFiles} />
                        <button className="button">
                            <i className="fi-arrow-up"></i>&nbsp;
                            Envoyer ces {this.state.files.length} fichiers sur DocHub
                        </button>
                    </div>
                </div>
            </div>
        );
    }
}
