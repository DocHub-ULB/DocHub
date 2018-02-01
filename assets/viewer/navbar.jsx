import React, { Component } from 'react';

export default class Navbar extends Component {
  render() {
    return (
        <div className="top-bar" id="navbar">
            <a className="button left" href='#'>Back</a>
            <a className="button left" href='#'>Download</a>
            <font color="white">{this.props.docname}</font>
            <button className="button right" onClick={this.props.zoomin}>Zoom</button>
            <button className="button right" onClick={this.props.zoomout}>De-zoom</button>
        </div>
    );
  }
}
