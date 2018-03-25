const React = require('react');
const Tag = require('./Tag.jsx');
import Cookies from 'js-cookie'

import {markdown} from 'markdown';
import moment from 'moment'
import PropTypes from 'prop-types';

import {UpvoteButton, DownvoteButton} from './Vote.jsx';

class CourseDocument extends React.Component{
    constructor(props) {
        super(props)
        this.state = {upvote_active: this.props.user_vote==1,
                      downvote_active: this.props.user_vote==-1,
                      upvotes: this.props.votes.upvotes,
                      downvotes: this.props.votes.downvotes
        };
        this.vote_callback = this.vote_callback.bind(this)
    }
    ready() {return (this.props.is_ready);}
    editable() {return this.props.has_perm;}
    date() {return moment(this.props.date).format("D MMMM YYYY");}
    edit_url() {return window.Urls.document_edit(this.props.id);}
    reupload_url() {return window.Urls.document_reupload(this.props.id);}
    url() {return window.Urls.document_show(this.props.id);}
    icon() {
        if (this.ready()){
            return (<a href={this.url()}>
                <i className="fi-page-copy round-icon big"></i>
            </a>);
        } else if (this.props.is_processing) {
            return <i className="fi-loop round-icon big"></i>;
        } else {
            return <i className="fi-save round-icon big"></i>;
        }
    }
    download_icon() {
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
    }
    edit_icon() {
        if (this.ready() && this.editable()){
            return
            <a href={this.edit_url()} title="Éditer">
                <i className="fi-pencil dark-grey"></i> Editer
            </a>;
        }
        return '';
    }
    reupload_icon() {
        if (this.ready() && this.editable()){
            return (<a href={this.reupload_url()}>
                <i className="fi-page-add dark-grey" title="Nouvelle version"></i> Ré-uploader
            </a>);
        }
    }
    upvote_icon() {
        return (<UpvoteButton doc_id={this.props.id} num={this.state.upvotes} isActive={this.state.upvote_active} vote_callback={this.vote_callback} />);

    }
    downvote_icon() {
        return (<DownvoteButton doc_id={this.props.id} num={this.state.downvotes} isActive={this.state.downvote_active} vote_callback={this.vote_callback}/>);
    }
    vote_callback() {
        $.get(window.Urls.document_detail(this.props.id), function (data) {
            this.setState({upvote_active: data.user_vote==1,
                            downvote_active: data.user_vote==-1,
                            upvotes: data.votes.upvotes,
                            downvotes: data.votes.downvotes});
        }.bind(this))
    }
    description() {
        var text = markdown.toHTML(this.props.description);
        if (text != ''){
            var wrap = {__html: text};
            return <p dangerouslySetInnerHTML={wrap} />;
        }
        return '';
    }
    title() {
        if (this.ready()){
            return <a href={this.url()}>{this.props.name}</a>;
        }
        return this.props.name;
    }
    pages() {
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
    }
    tags() {
        return this.props.tags.map(function(tag){
            return <Tag key={"tag"+tag.id} {...tag}/>
        });
    }
    render() {
        return (<div className="row course-row document">
            {this.icon()} {this.upvote_icon()} {this.downvote_icon()}
            <div className="cell course-row-content">
                <h5>
                    {this.title()}
                    <small> par {this.props.user.name}</small><br/>
                </h5>
                {this.description()}
                {this.download_icon()} {this.edit_icon()} {this.reupload_icon()}
                <div className="course-content-last-line">
                    <i className="fi-page-filled"></i> {this.pages()}&nbsp;
                    <i className="fi-clock"></i> Uploadé le {this.date()}&nbsp;
                    <i className="fi-pricetag-multiple"></i> {this.tags()}
                </div>
            </div>
        </div>);
    }
};

export default CourseDocument;
