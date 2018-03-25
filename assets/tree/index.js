const React = require('react');
const ReactDOM = require('react-dom');
const Menu = require('./menu.js');

window.courseTreeRender = (data) => {
    ReactDOM.render(
        <Menu {...data[0]}/>,
        document.getElementById('course-tree-menu')
    );
};
