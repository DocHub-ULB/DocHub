const React = require('react');
const ReactDOM = require('react-dom');
const Menu = require('./menu.js');
const SideTree = require('./sidetree.js');

window.courseTreeRender = (data) => {
    ReactDOM.render(
        <Menu {...data[0]}/>,
        document.getElementById('course-tree-menu')
    );
    ReactDOM.render(
        <SideTree content={data}/>,
        document.getElementById('side-tree-menu')
    );
};
