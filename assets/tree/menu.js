const React = require('react');
const ReactDOM = require('react-dom');
const Category = require('./category.js');


class Menu extends React.Component {
    constructor (props) {
        super(props);
    }

    render () {
        items = this.props.children.map((fac) => {
            return (
                <Category {...fac} key={fac.id}/>
            )
        });

        return (
            <ul className="left">
                {items}
            </ul>
        );
    }
}

module.exports = Menu;
