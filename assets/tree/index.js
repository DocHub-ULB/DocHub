const React = require('react');
const ReactDOM = require('react-dom');
const Menu = require('./menu.js');
const SideTree = require('./sidetree.js');

window.courseTreeRender = (data) => {
    ReactDOM.render(
        <SideTree content={data[0].children}/>,
        document.getElementById('side-tree-menu')
    );
};
