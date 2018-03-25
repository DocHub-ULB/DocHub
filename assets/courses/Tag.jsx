const React = require('react');

class Tag extends React.Component {
    id = () => this.props.id
    name = () => this.props.name
    color = () => this.props.color
    clicked = () => {if (this.props.onClick) this.props.onClick(this)}
    render = function(){
        var style = {border: 'solid 2px ' + this.color()};
        var klass = "radius label tag-item";
        var icon = "";
        if (this.props.active){
            klass += " active";
            style['color'] = this.color();
            style['backgroundColor'] = 'white';
            icon = (<i className="fi-check"> </i>)
        } else {
            style['backgroundColor'] = this.color();
            style['color'] = 'white';
            icon = (<i className="fi-stop"> </i>)
        }

        if (this.props.onClick){
            klass += " selectionable";
        } else {
            icon = "";
        }
        return (<span>
            <span onClick={this.clicked}
                        style={style} className={klass}>
            {icon}
            {this.name()}
            </span>&nbsp;
        </span>);
    }
}

module.exports = Tag;
