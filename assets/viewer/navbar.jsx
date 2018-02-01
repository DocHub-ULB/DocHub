import React, { Component } from 'react';

export default class Navbar extends Component {
  render() {
    return (
        <div className="top-bar" id="navbar">
            <a className="button left" href='#'>Back</a>
            <a className="button left" href='#'>Download</a>
            <a className="button" href='#'>Name</a>
            <a className="button right" onClick={this.props.zoomin}>Zoom</a>
            <a className="button right" onClick={this.props.zoomout}>De-zoom</a>
        </div>
    );
  }
}
