import React, { Component } from 'react';

export default class Navbar extends Component {
  render() {
    return (
        <div className="sticky">
            <nav className="top-bar" id="navbar">
                <a className="button navbar-button left" href={window.Urls.course_show(this.props.course_name)}>
                  <i className="fi-arrow-left"></i> {this.props.course_name}
                </a>

                <a className="button navbar-button left" href={window.Urls.document_download(this.props.docid)}>
                  <i className="fi-download"></i> Télécharger - PDF
                </a>

                {this.props.original != this.props.pdf?
                    (<a className="button navbar-button left" href={window.Urls.document_download_original(this.props.docid)}>
                      <i className="fi-download"></i> Télécharger - Original
                    </a>)
                    :null}

                <font color="white">{this.props.docname}</font>

                {this.props.has_perm?
                    (<a className="button navbar-button right" href={window.Urls.document_edit(this.props.docid)}>
                      <i className="fi-pencil"></i> Editer
                    </a>)
                    :null}


                <button className="button navbar-button right" onClick={this.props.zoomin}>
                  <i className="fi-zoom-in"></i> Zoom
                </button>

                <button className="button navbar-button right" onClick={this.props.zoomout}>
                  <i className="fi-zoom-out"></i> De-zoom
                </button>

            </nav>
        </div>
    );
  }
}
