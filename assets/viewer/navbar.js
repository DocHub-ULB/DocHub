import React, { Component } from 'react';

var menuIconStyle = {
    paddingright: "1em"
}

export default class Navbar extends Component {
  render() {
    return (
        <div className="sticky contain-to-grid">
            <nav className="top-bar" id="navbar" data-topbar="">

                <ul className="title-area">
                    <li className="name">
                       <h2><a href="#">{this.props.docname}</a></h2>
                    </li>

                    <li className="toggle-topbar menu-icon">
                        <a href="#" style={menuIconStyle}>
                            Menu <i className="fi-list"></i>
                        </a>
                    </li>
                </ul>

                <section className="top-bar-section">
                <ul className="left">
                    <li>
                        <a className="" href={window.Urls.course_show(this.props.course_name)}>
                          <i className="fi-arrow-left"></i> {this.props.course_name}
                        </a>
                    </li>

                    {this.props.is_pdf == "True"?
                        (<li>
                            <a  href={window.Urls['document-pdf'](this.props.docid)}>
                            <i className="fi-download"></i> Télécharger
                            </a>
                            </li>)
                        :
                        (<li className="has-dropdown">
                            <a href="#">
                            <i className="fi-download"></i> Télécharger
                            </a>
                            <ul className="dropdown">
                            <li>
                            <a href={window.Urls['document-original'](this.props.docid)}>
                            Original
                            </a>
                            </li>

                            <li>
                            <a href={window.Urls['document-pdf'](this.props.docid)}>
                            PDF
                            </a>
                            </li>
                            </ul>
                            </li>)
                    }
                </ul>
                <ul className="right">
        <li><ul className="button-group navbar-button">
                {this.props.has_perm == "1"?
                    (<li><a className="button navbar-button" href={window.Urls.document_edit(this.props.docid)}>
                      <i className="fi-pencil"></i>
                    </a></li>)
                    :null}

                <li>
                <a className="button navbar-button" href="#" onClick={this.props.zoomin}>
                  <i className="fi-zoom-in"></i>
                </a>
                </li>

                <li>
                <a className="button navbar-button" href="#" onClick={this.props.zoomout}>
                  <i className="fi-zoom-out"></i>
                </a>
                </li>
        </ul>
        </li>
                </ul>
                </section>
            </nav>
        </div>
    );
  }
}
