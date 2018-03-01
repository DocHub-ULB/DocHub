const React = require('react');
const Tag = require('./Tag.jsx');
import Cookies from 'js-cookie'

import {markdown} from 'markdown';
import moment from 'moment'
import PropTypes from 'prop-types';

class VoteButton extends React.Component {
    constructor(props) {
        super(props)
        this.clicked = this.clicked.bind(this)
    }
    clicked(e) {
        e.preventDefault();
        if (!this.props.isActive){
            // https://briancaffey.github.io/2017/07/22/posting-json-data-with-ajax-to-django-rest-framework.html
            $.ajax({
                type : "POST",
                url : this.props.request_url,
                data : JSON.stringify({"doc_id": this.props.doc_id, "vote": this.props.vote_type}),
                headers: {
                  'Accept': 'application/json',
                  'Content-Type': 'application/json',
                  'X-CSRFToken': this.csrf_token(),
                  },
                success: function(response){
                    this.props.vote_callback(response);
                }.bind(this)
            });
        }
    }
    pretty_vote_num() {
        if (this.props.num < 1000){
            return this.props.num.toString();
        }else{
            return ((this.props.num / 1000).toString()).slice(0,3) + "k"
        }
    }
    csrf_token() {
        return Cookies.get('csrftoken')
    }
    render() {
        return (
            <div>
            <span onClick={this.clicked}>
                <i className={`${this.props.icon_class} ${this.props.isActive ? 'active' : ''}`}></i>
            </span>
            <span className={this.props.label_class}>{this.pretty_vote_num()}</span>
            </div>
        );
    }
};

VoteButton.propTypes = {
    request_url: PropTypes.string.isRequired,
    vote_type: PropTypes.string.isRequired,
    icon_class: PropTypes.string.isRequired,
    label_class: PropTypes.string.isRequired,
    isActive: PropTypes.bool.isRequired,
    vote_callback: PropTypes.func.isRequired,
    num: PropTypes.number.isRequired
}

class UpvoteButton extends React.Component {
    render() {
        return (        // isActive, vote_callback, num
            <VoteButton {...this.props}
                request_url={window.Urls.upvote_document()}
                vote_type={"up"}
                label_class={"round success label votelabel"}
                icon_class={"fi-like round-icon medium upvote"}
            />
        );
    }
};

class DownvoteButton extends React.Component{
    render() {
        return (        // isActive, vote_callback, num
            <VoteButton {...this.props}
                request_url={window.Urls.downvote_document()}
                vote_type={"down"}
                label_class={"round alert label votelabel"}
                icon_class={"fi-dislike round-icon medium downvote"}
            />
        );
    }
};

const CourseDocument = React.createClass({
    getInitialState: function(){
        return {upvote_active: this.props.user_vote==1,
                downvote_active: this.props.user_vote==-1,
                upvotes: this.props.votes.upvotes,
                downvotes: this.props.votes.downvotes};
    },
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
        return (<UpvoteButton doc_id={this.props.id} num={this.state.upvotes} isActive={this.state.upvote_active} vote_callback={this.upvote_callback} />);

    },
    downvote_icon: function(){
        return (<DownvoteButton doc_id={this.props.id} num={this.state.downvotes} isActive={this.state.downvote_active} vote_callback={this.downvote_callback}/>);
    },
    downvote_callback: function(response){
        var new_downvotes = this.state.downvotes + 1
        var new_upvotes = this.state.upvotes - (response.created ? 0 : 1)
        this.setState({upvote_active: false,
                        downvote_active: true,
                        upvotes: new_upvotes,
                        downvotes: new_downvotes,});
    },
    upvote_callback: function(response){
        var new_upvotes = this.state.upvotes + 1
        var new_downvotes = this.state.downvotes - (response.created ? 0 : 1)
        this.setState({upvote_active: true,
                        downvote_active: false,
                        upvotes: new_upvotes,
                        downvotes: new_downvotes,});
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
});

export default CourseDocument;
