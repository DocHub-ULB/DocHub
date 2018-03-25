const React = require('react');

class Course extends React.Component {
    constructor (props) {
        super(props);
    }

    url () {
        return Urls.course_show(this.props.slug);
    }

    render () {
        return (
            <li>
                <a href={this.url()}>
                    {this.props.slug}: <strong>{this.props.name}</strong>
                </a>
            </li>
        );
    }
}

module.exports = Course;
