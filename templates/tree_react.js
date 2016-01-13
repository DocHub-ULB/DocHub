const Course = React.createClass({
    base_url: '{% url "course_show" slug="__TEMPLATE__" %}',
    url: function(){
        return this.base_url.replace('__TEMPLATE__', this.props.slug);
    },
    render: function(){
        return <li><a href={this.url()}>
            {this.props.slug}: <strong>{this.props.name}</strong>
        </a></li>;
    }
});

const Category = React.createClass({
    base_url: '{% url "category_show" pk=424242424242 %}',
    url: function(){
        return this.base_url.replace('424242424242', this.props.id);
    },
    render: function(){
        var children = this.props.children.map(function(cat){
            return <Category key={"cat"+cat.id} {...cat}/>;
        });
        var courses = this.props.courses.map(function(course){
            return <Course key={"course"+course.id} {...course}/>;
        });
        var contents = "";
        if (children.length > 0 || courses.length > 0){
            contents = <ul className="dropdown">
                {children}
                <li className="divider"></li>
                {courses}
            </ul>;
        }
        return <li className="has-dropdown">
            <a href={this.url()}>{this.props.name}</a>
            {contents}
        </li>;
    }
});

$(document).ready(function(){
    $(document).foundation();
    $.get('{% url "course_tree" %}', function(data){
        ReactDOM.render(<Category {...data[0]}/>,
            document.getElementById('course-tree-menu')
        );
        $(document).foundation('topbar', 'reflow');
    });
});