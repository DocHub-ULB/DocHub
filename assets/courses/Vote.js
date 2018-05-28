const React = require('react');
const Tag = require('./Tag.js');
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
                url : window.Urls.document_vote(this.props.doc_id),
                data : JSON.stringify({"vote_type": this.props.vote_type}),
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
            return ((this.props.num / 1000).toFixed(1).toString()) + "k"
        }
    }
    csrf_token() {
        return Cookies.get('csrftoken')
    }
    render() {
        let res =  <a title={this.props.description} className={"label radius " + (this.props.isActive ? 'info' : 'secondary')} onClick={this.clicked}>
            <i className={`${this.props.icon_class} ${this.props.isActive ? 'active' : ''}`}></i>
            &nbsp;
            {this.pretty_vote_num()}
        </a>;
        return res;
    }
};

VoteButton.propTypes = {
    vote_type: PropTypes.string.isRequired,
    icon_class: PropTypes.string.isRequired,
    label_class: PropTypes.string.isRequired,
    isActive: PropTypes.bool.isRequired,
    vote_callback: PropTypes.func.isRequired,
    num: PropTypes.number.isRequired
}

export class UpvoteButton extends React.Component {
    render() {
        return (        // isActive, vote_callback, num
            <VoteButton {...this.props}
                vote_type={"up"}
                label_class={"round success label votelabel"}
                icon_class={"fi-like round-icon medium upvote"}
                description="Ce document est très utile et mérite plus d'attention"
            />
        );
    }
};

export class DownvoteButton extends React.Component{
    render() {
        return (        // isActive, vote_callback, num
            <VoteButton {...this.props}
                vote_type={"down"}
                label_class={"round alert label votelabel"}
                icon_class={"fi-dislike round-icon medium downvote"}
                description="Ce document est décevant et/ou inintéressant pour le cours"
            />
        );
    }
};
