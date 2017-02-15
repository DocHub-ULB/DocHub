const React = require('react');
const ReactDOM = require('react-dom');
const Category = require('./category.jsx');

window.courseTreeRender = (data) => {                                                                                                                                             
    ReactDOM.render(
        <Category {...data[0]}/>,
        document.getElementById('course-tree-menu')
    );
};
