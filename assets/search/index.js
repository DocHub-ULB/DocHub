const React = require('react');
const ReactDOM = require('react-dom');
const Search = require('./Search.js').default;

window.onload = () => {
  ReactDOM.render(
    <Search/>,
    document.getElementById('react-search')
  );
};
