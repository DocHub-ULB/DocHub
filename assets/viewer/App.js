import React, { Component } from 'react';
import { Document, Page } from 'react-pdf/build/entry.webpack';

class Loader extends Component {
    render () {
        return (<div className="viewer-loader">LOAD</div>)
    }
}

export default class App extends Component {
  state = {
    numPages: null,
    pageNumber: 1,
    view_more: 1
  }

  onDocumentLoad = ({ numPages }) => {
    this.setState({ numPages });
  }

  view_more() {
      this.setState({view_more: this.state["view_more"] + 1})
  }

  render() {
    const { pageNumber, numPages, view_more } = this.state;

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

    return (
      <div className="viewer">
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
                  width={1000}
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
