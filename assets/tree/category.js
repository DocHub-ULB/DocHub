const React = require('react');
const Course = require('./course.js');

class Category extends React.Component {
    constructor (props) {
        super(props);
    }

    url () {
        return Urls.category_show(this.props.id);
    }

    render () {
        const children = this.props.children.map(function(cat){
            return <Category key={"cat"+cat.id} {...cat}/>;
        });
        const courses = this.props.courses.map(function(course){
            return <Course key={"course"+course.id} {...course}/>;
        });
        let contents = "";
        if (children.length > 0 || courses.length > 0){
            contents = (
                <ul className="dropdown">
                    {children}
                    <li className="divider"></li>
                    {courses}
                </ul>
            );
        }

        return (
            <li className="has-dropdown">
                <a href={this.url()}>{this.props.name}</a>
                {contents}
            </li>
        );
    }
}

module.exports = Category;
