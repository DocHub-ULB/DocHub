const Course = React.createClass({
    url: function(){
        return Urls.course_show(this.props.slug);
    },
    render: function(){
        return <li><a href={this.url()}>
            {this.props.slug}: <strong>{this.props.name}</strong>
        </a></li>;
    }
});

const Category = React.createClass({
    url: function(){
        return Urls.category_show(this.props.id);
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
    $.get(Urls.course_tree(), function(data){
        ReactDOM.render(<Category {...data[0]}/>,
                        document.getElementById('course-tree-menu')
        );
        $(document).foundation('topbar', 'reflow');
    });
});