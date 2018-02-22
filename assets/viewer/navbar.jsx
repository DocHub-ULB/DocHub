import React, { Component } from 'react';

const buttonStyle = {
  "backgroundColor":'rgba(51, 51, 51, 1)',
}

export default class Navbar extends Component {
  render() {
    return (
        <div className="sticky">
            <nav className="top-bar" id="navbar">
                <a className="button left" href={"/catalog/course/" + this.props.couname} style={buttonStyle}>
                  <i className="fi-arrow-left"></i> {this.props.couname}
                </a>

                <a className="button left" href={window.Urls.document_download(this.props.docid)} style={buttonStyle}>
                  <i className="fi-download"></i> Download
                </a>

                <font color="white">{this.props.docname}</font>

                <button className="button right" onClick={this.props.zoomin} style={buttonStyle}>
                  <i className="fi-zoom-in"></i> Zoom
                </button>

                <button className="button right" onClick={this.props.zoomout} style={buttonStyle}>
                  <i className="fi-zoom-out"></i> De-zoom
                </button>

            </nav>
        </div>
    );
  }
}
