import React, { Component } from 'react';
import { Document, Page } from 'react-pdf/build/entry.webpack';
import Navbar from './navbar';

class Loader extends Component {
    render () {
        return (<div className="viewer-loader">LOAD</div>)
    }
}

export default class App extends Component {
  state = {
    numPages: null,
    pageNumber: 1,
    view_more: 1,
    zoomlevel: 1.2
  }

  onDocumentLoad = ({ numPages }) => {
    this.setState({ numPages });
  }

  view_more() {
      this.setState({view_more: this.state["view_more"] + 1})
  }

  zoomin(){
    this.setState({zoomlevel: this.state.zoomlevel + 0.1})
  }

  zoomout(){
    this.setState({zoomlevel: this.state.zoomlevel - 0.1})
  }

  render() {
    const { pageNumber, numPages, view_more, zoomlevel} = this.state;

    const renderPages = Math.min(5 * view_more, numPages);

    var render_not_full = ""
    if (renderPages < numPages) {
        render_not_full = (
            <button className="viewer-show-more btn" onClick={this.view_more.bind(this)}>
                This document has {numPages - renderPages} more pages. Click to view more.
            </button>
        );
    }

    var url = document.getElementById('pdf-url').dataset.url
    var name = document.getElementById('pdf-url').dataset.name
    var id = document.getElementById('pdf-url').dataset.id
    var coursename = document.getElementById('pdf-url').dataset.coursename

    return (
      <div className="viewer">
        <Navbar zoomin={this.zoomin.bind(this)} zoomout={this.zoomout.bind(this)} docname={name} docid={id} couname={coursename}/>
        <Document
          className="viewer-document"
          file={url}
          onLoadSuccess={this.onDocumentLoad}
          loading={<Loader />}
        >
            {
            Array.from(
              new Array(renderPages),
              (el, index) => (
                <Page
                  key={`page_${index + 1}`}
                  pageNumber={index + 1}
                  renderTextLayer={false}
                  scale={zoomlevel}
                />

              ),
            )
            }
        </Document>
        {render_not_full}
      </div>
    );
  }
}
