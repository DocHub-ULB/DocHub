const React = require('react');
const ReactDOM = require('react-dom');
const CourseDocumentList = require('./CourseDocumentList.jsx');

window.loadCourseViewer = (dest, data) => {
    ReactDOM.render(
        <CourseDocumentList {...data} />,
        document.getElementById(dest)
    );
};
