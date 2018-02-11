const React = require('react');
const CourseDocument = require('./CourseDocument.jsx').default;
const Tag = require('./Tag.jsx');

/* http://stackoverflow.com/questions/728360/most-elegant-way-to-clone-a-javascript-object */
const clone = function(obj){
    var copy;
    if (null == obj || "object" != typeof obj) return obj;
    if (obj instanceof Date){
        copy = new Date();
        copy.setTime(obj.getTime());
        return copy;
    }
    if (obj instanceof Array){
        copy = [];
        for (var i=0, len=obj.length; i<len; i++){copy[i] = clone(obj[i]);}
        return copy;
    }
    if (obj instanceof Object){
        copy = {};
        for (var attr in obj){
            if (obj.hasOwnProperty(attr)){copy[attr] = clone(obj[attr]);}
        }
        return copy;
    }
    throw new Error("Unable to copy obj! Its type isn't supported.");
}

const CourseDocumentList = React.createClass({
    getInitialState: function(){
        return {
            tag_filter: [],
            search_text: ""
        };
    },
    has_tag: function(doc, tag){
        for (var i=0; i<doc.tags.length; i++){
            if (doc.tags[i].id == tag.id){
                return true;
            }
        }
        return false;
    },
    tags_in_documents: function(){
        var res = {};
        this.props.document_set.map(function(doc){
            doc.tags.map(function(t){res[t.id] = t;});
        });
        return clone(Object.keys(res).map(function(k){return res[k];}));
    },
    tag_clicked: function(tag){
        var t = tag.id();
        var i = this.state.tag_filter.indexOf(t);
        if (i >= 0){
            var before = this.state.tag_filter.slice(0, i);
            var after = this.state.tag_filter.slice(i+1);
            this.setState({tag_filter: before.concat(after)});
        } else {
            this.setState({
                tag_filter: this.state.tag_filter.concat([t])
            });
        }
    },
    search_changed: function(evt){
        this.setState({search_text: evt.target.value});
    },
    documents_filtered: function(){
        var pattern = new RegExp(this.state.search_text, 'i');
        return this.props.document_set.filter(function(doc){
            return doc.hidden == false;
        }).filter(function(doc){
            if (doc.name.search(pattern) < 0){
                return false;
            }
            var admissible = true;
            var dtags = doc.tags.map(function(tag){return tag.id;});
            this.state.tag_filter.map(function(tag){
                if (dtags.indexOf(tag) < 0){
                    admissible = false;
                }
            });
            return admissible;
        }.bind(this)).sort(function(a, b){return a.date >= b.date;});
    },
    tag_bar: function(){
        return this.tags_in_documents().map(function(tag){
            var occurences = this.documents_filtered()
                                 .map(function(x){return this.has_tag(x, tag);}.bind(this))
                                 .reduce(function(x, y){return x+y;}, 0);
            tag.active = (this.state.tag_filter.indexOf(tag.id) >= 0);
            tag.name += " (" + occurences + ")";
            return <Tag key={"tag"+tag.id} onClick={this.tag_clicked} {...tag}/>;
        }.bind(this));
    },
    render: function(){
        var docs = this.documents_filtered().map(function(doc){
            return <CourseDocument key={"doc"+doc.id} {...doc} />;
        });

        return (<div>
            <div className="row">
                <div className="column small-7">
                    <h3>Filtrer <small>par tag</small></h3>
                    {this.tag_bar()}
                </div>
                <div className="column small-5">
                    <h3>Chercher <small>dans le titre</small></h3>
                    <input type="text" onChange={this.search_changed}/>
                </div>
            </div>
            <hr/>
            {docs}
        </div>);
    }
});

export default CourseDocumentList;
