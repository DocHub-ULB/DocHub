const React = require('react');

const CourseDocument = React.createClass({
    ready: function(){return (this.props.state == 'DONE');},
    editable: function(){return this.props.has_perm;},
    date: function(){return moment(this.props.date).format("D MMMM YYYY");},
    edit_url: function(){return Urls.document_edit(this.props.id);},
    reupload_url: function(){return Urls.document_reupload(this.props.id);},
    url: function(){return Urls.document_show(this.props.id);},
    icon: function(){
        if (this.ready()){
            return <a href={this.url()}>
                <i className="fi-page-copy round-icon big"></i>
            </a>;
        }
        return <i className="fi-loop round-icon big"></i>;
    },
    download_icon: function(){
        if (this.ready()){
            return <a href={Urls.document_download(this.props.id)} title="Télécharger">
                <i className="fi-download"></i>
            </a>
        }
        return ''
    },
    edit_icon: function(){
        if (this.ready() && this.editable()){
            return <a href={this.edit_url()} title="Éditer">
                <i className="fi-pencil dark-grey"></i>
            </a>;
        }
        return '';
    },
    reupload_icon: function(){
        if (this.ready() && this.editable()){
            return <a href={this.reupload_url()}>
                <i className="fi-page-add dark-grey" title="Nouvelle version"></i>
            </a>;
        }
    },
    description: function(){
        var text = markdown.toHTML(this.props.description);
        if (text != ''){
            var wrap = {__html: text};
            return <p dangerouslySetInnerHTML={wrap} />;
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
    tags: function(){
        return this.props.tags.map(function(tag){
            return <Tag key={"tag"+tag.id} {...tag}/>
        });
    },
    render: function(){
        return <div className="row course-row document">
            {this.icon()}
            <div className="course-row-content">
                <h5>
                    {this.title()}
                    <small> par {this.props.user.name}</small><br/>
                    {this.download_icon()} {this.edit_icon()} {this.reupload_icon()}
                </h5>
                {this.description()}
                <div className="course-content-last-line">
                    <i className="fi-page-filled"></i> {this.pages()}&nbsp;
                    <i className="fi-clock"></i> Uploadé le {this.date()}&nbsp;
                    <i className="fi-pricetag-multiple"></i> {this.tags()}
                </div>
            </div>
        </div>;
    }
});

module.exports = CourseDocument;
