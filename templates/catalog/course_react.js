const Document = React.createClass({
    ready: function(){return (this.props.state == 'DONE');},
    editable: function(){return this.props.has_perm;},
    date: function(){return moment(this.props.date).format("D MMMM YYYY");},
    edit_url: function(){
        return "{% url 'document_edit' 4242424242 %}".replace('4242424242', this.props.id);
    },
    url: function(){
        return "{% url 'document_show' 4242424242 %}".replace('4242424242', this.props.id);
    },
    icon: function(){
        if (this.props.state == 'DONE'){
            return <a href={this.url()}>
                <i className="fi-page-copy round-icon big"></i>
            </a>;
        }
        return <i className="fi-loop round-icon big"></i>;
    },
    edit_icon: function(){
        if (this.ready() && this.editable()){
            return <a href={this.edit_url()}>
                <i className="fi-pencil dark-grey"></i>
            </a>;
        }
        return '';
    },
    description: function(){
        if (this.props.description != ''){
            return <p>{this.props.description}</p>;
        }
        return '';
    },
    title: function(){
        if (this.ready()){
            return <a href={this.url()}>{this.props.name}</a>; 
        }
        return this.props.name;
    },
    pages: function(){
        if (! this.ready()){
            return "En cours de traitement";
        }
        else if (this.props.pages == 1){
            return "1 page";
        }
        return this.props.pages + " pages";
    },
    render: function(){
        return <div className="row course-row document">
            {this.icon()}
            <div className="course-row-content">
                <h5>
                    {this.title()} {this.edit_icon()}
                    <small> par {this.props.user.name}</small>
                </h5>
                {this.description()}
                <div className="course-content-last-line">
                    <i className="fi-page-filled"></i> {this.pages()} &nbsp;
                    <i className="fi-clock"></i> Uploadé le {this.date()}
                </div>
            </div>
        </div>;
    }
});

const DocumentList = React.createClass({
    render: function(){
        var docs = this.props.document_set.map(function(doc){
            console.log(doc);
            return <Document {...doc} />;
        });
        return <div>{docs}</div>;
    }
});

$(document).ready(function(){
    $.get('{% url "course-detail" slug=course.slug %}', function(course){
        ReactDOM.render(<DocumentList {...course}/>,
                    document.getElementById('documents'));
    });
});
