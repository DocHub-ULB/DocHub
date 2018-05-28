const React = require('react');
const ReactDOM = require('react-dom');
const CourseDocumentList = require('./CourseDocumentList.js').default;

document.addEventListener("DOMContentLoaded",function(){
    window.loadCourseViewer = (dest, data) => {
        ReactDOM.render(
            <CourseDocumentList {...data} />,
            document.getElementById(dest)
        );
    };
});
