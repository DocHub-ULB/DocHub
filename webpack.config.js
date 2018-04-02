var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');
var webpack = require('webpack');

module.exports = {
    context: __dirname,

    devtool: "eval-source-map",

    entry: {
        tree: [
            './assets/tree/index.js',
        ],
        courses: [
            './assets/courses/index.js',
        ],
        viewer: [
            './assets/viewer/index.js',
        ],
        uploader: [
            './assets/uploader/index.js',
        ],
        styles: [
            './assets/styles/index.js',
        ],
    },

    output: {
        path: path.resolve('./static/scripts/'),
        filename: '[name]-[hash].js',
        publicPath: "/static/scripts/",
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
    ],

    optimization: {
        splitChunks: {
            cacheGroups: {
                commons: {
                    name: "commons",
                    chunks: "initial",
                    minChunks: 2
                }
            }
        },
    },

    module: {
        rules: [
            {
                test: /\.js?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                options: {
                    presets:[
                        ['es2015', {modules: false}],
                        'stage-0',
                        'react'
                    ],
                },
            },
            {
                test: /\.css$/,
                loaders: ['style-loader', 'css-loader'],
            },
            {
                test: /\.sass?$/,
                loaders: ['style-loader', 'css-loader', 'sass-loader']
            },
        ],
    },

    resolve: {
        modules: ['node_modules'],
        extensions: ['.js']
    },
};
