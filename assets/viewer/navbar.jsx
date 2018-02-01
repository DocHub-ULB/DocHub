import React, { Component } from 'react';

export default class Navbar extends Component {
  render() {
    return (
        <div className="top-bar" id="navbar">
            <a className="button left" href='#'><i className="fi-arrow-left"></i>Back</a>
            <a className="button left" href='#'><i className="fi-download"></i>Download</a>
            <font color="white">{this.props.docname}</font>
            <button className="button right" onClick={this.props.zoomin}><i className="fi-zoom-in"></i>Zoom</button>
            <button className="button right" onClick={this.props.zoomout}><i className="fi-zoom-out"></i>De-zoom</button>
        </div>
    );
  }
}
