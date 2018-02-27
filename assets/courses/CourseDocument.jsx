const React = require('react');
const Tag = require('./Tag.jsx');
window.Cookies = require('js-cookie');

import {markdown} from 'markdown';
import moment from 'moment'

const UpvoteButton = React.createClass({
    clicked: function(e){
        e.preventDefault();
        // https://briancaffey.github.io/2017/07/22/posting-json-data-with-ajax-to-django-rest-framework.html
        $.ajax({
            type : "POST",
            url : window.Urls.upvote_document(),
            data : JSON.stringify({"doc_id": this.props.doc_id}),
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'X-CSRFToken': this.csrf_token()
              },
        });
    },
    csrf_token: function(){
        return Cookies.get('csrftoken')},
    render: function(){
            return (
                <span onClick={this.clicked}>
                    <i className="fi-like round-icon medium upvote"></i>
                </span>);
        }
});

const DownvoteButton = React.createClass({
    clicked: function(e){
        e.preventDefault();
        // https://briancaffey.github.io/2017/07/22/posting-json-data-with-ajax-to-django-rest-framework.html
        $.ajax({
            type : "POST",
            url : window.Urls.downvote_document(),
            data : JSON.stringify({"doc_id": this.props.doc_id}),
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json',
              'X-CSRFToken': this.csrf_token()
              },
        });
    },
    csrf_token: function(){return Cookies.get('csrftoken')},
    render: function(){
            return (
                <span onClick={this.clicked}>
                    <i className="fi-dislike round-icon medium downvote"></i>
                </span>);
        }
});

const CourseDocument = React.createClass({
    ready: function(){return (this.props.is_ready);},
    editable: function(){return this.props.has_perm;},
    date: function(){return moment(this.props.date).format("D MMMM YYYY");},
    edit_url: function(){return window.Urls.document_edit(this.props.id);},
    reupload_url: function(){return window.Urls.document_reupload(this.props.id);},
    url: function(){return window.Urls.document_show(this.props.id);},
    icon: function(){
        if (this.ready()){
            return (<a href={this.url()}>
                <i className="fi-page-copy round-icon big"></i>
            </a>);
        } else if (this.props.is_processing) {
            return <i className="fi-loop round-icon big"></i>;
        } else {
            return <i className="fi-save round-icon big"></i>;
        }
    },
    download_icon: function(){
        if (this.ready()){
            var url = window.Urls.document_download(this.props.id)
        } else {
            var url = window.Urls.document_download_original(this.props.id)
        }
        return (
            <a href={url} title="Télécharger">
                <i className="fi-download dark-grey"></i> Télécharger
            </a>
        )
    },
    edit_icon: function(){
        if (this.ready() && this.editable()){
            return
            <a href={this.edit_url()} title="Éditer">
                <i className="fi-pencil dark-grey"></i> Editer
            </a>;
        }
        return '';
    },
    reupload_icon: function(){
        if (this.ready() && this.editable()){
            return (<a href={this.reupload_url()}>
                <i className="fi-page-add dark-grey" title="Nouvelle version"></i> Ré-uploader
            </a>);
        }
    },
    upvote_icon: function(){
        return (<UpvoteButton doc_id={this.props.id} />);

    },
    downvote_icon: function(){
        return (<DownvoteButton doc_id={this.props.id} />);
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
        else if (this.props.is_unconvertible){
            return "";
        }
        return this.props.pages + " pages";
    },
    tags: function(){
        return this.props.tags.map(function(tag){
            return <Tag key={"tag"+tag.id} {...tag}/>
        });
    },
    render: function(){
        console.log(this.props)
        return (<div className="row course-row document">
            {this.icon()}
            <div className="cell course-row-content">
                <h5>
                    {this.title()}
                    <small> par {this.props.user.name}</small><br/>
                </h5>
                {this.description()}
                {this.download_icon()} {this.edit_icon()} {this.reupload_icon()} {this.upvote_icon()} {this.downvote_icon()}
                <div className="course-content-last-line">
                    <i className="fi-page-filled"></i> {this.pages()}&nbsp;
                    <i className="fi-clock"></i> Uploadé le {this.date()}&nbsp;
                    <i className="fi-pricetag-multiple"></i> {this.tags()}
                </div>
            </div>
        </div>);
    }
});

export default CourseDocument;
