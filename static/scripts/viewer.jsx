const white = "/static/images/white.png";

const pageSize = function(zoom){
    return [parseInt(600 * zoom), parseInt(zoom * this.height_600)];
};

const aspectRatio = function(){
    return 900.0/this.height_900;
};

const PageObj = function(page){
    page.pageSize = pageSize.bind(page);
    page.aspectRatio = aspectRatio.bind(this);
    return page;
};

const Page = React.createClass({
    img_url: function(){
        if (! this.props.visible){return white;}
        if (this.props.width <= 120){return this.props.bitmap_120;}
        if (this.props.width <= 600){return this.props.bitmap_600;}
        return this.props.bitmap_900;
    },
    render: function(){
        var size = this.props.pageSize(1);
        var identifier = "page-"+this.props.numero;
        var style = {
            width: size[0]+'px',
            height: size[1]+'px',
            display: "block"
        };
        return <div className="row">
            <div className="medium-2 columns">

            </div>
            <div className="medium-10 columns">
                <a style={style} id={identifier} href={'#'+identifier}>
                    <img className="page" height={size[1]}
                         width={size[0]} src={this.img_url()}/>
                </a>
            </div>
        </div>;
    }
});

const PAGES_PADDING = 12;

const DocumentViewer = React.createClass({
    /* Return the index of the first (partially) visible page */
    topPageIndex: function(){
        var top = $(document).scrollTop();
        var acc = 0;
        var n = this.props.pages.length;
        for (var i=0; i<n; i++){
            var s = this.props.pages[i].pageSize(1);
            acc += s[1] + PAGES_PADDING;
            if (acc > top){
                return i;
            }
        }
        return n;
    },
    getInitialState: function(){
        return {zoom: 1, firstVisible: 0};
    },
    componentDidMount: function(){
        $(window).scroll(function(evt){
            var firstVisible = this.topPageIndex();
            this.setState({firstVisible: firstVisible});
        }.bind(this));
    },
    shouldComponentUpdate: function(nextProps, nextState) {
        return (! (_.isEqual(nextState, this.state) &&
                   _.isEqual(nextProps, this.props)));
    },
    render: function(){
        var firstVisible = this.state.firstVisible;
        var pages = this.props.pages.map(function(p, i){
            var v = Math.abs(i - firstVisible) <= 5;
            return <Page key={p.numero} visible={v} {...p}/>;
        }.bind(this));
        return <div id="pages">
            {pages}
        </div>;
    }
});

const loadDocumentViewer = function(dest){
    $(document).ready(function(){
        var doc_id = $('#'+dest).attr('data-id');
        $.get(Urls['page-set-list'](doc_id), function(data){
            var pages = data['results'].map(PageObj);
            ReactDOM.render(<DocumentViewer pages={pages} />,
                            document.getElementById(dest));
        });
    });
};

