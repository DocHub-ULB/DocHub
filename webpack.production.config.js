var path = require("path");
var webpack = require('webpack');
var BundleTracker = require('webpack-bundle-tracker');
// var ExtractTextPlugin = require('extract-text-webpack-plugin');

module.exports = {
  context: __dirname,

  entry: {
    tree: [
      './assets/tree/index.jsx',
    ],
    courses: [
      './assets/courses/index.jsx',
    ],
  },

  output: {
    path: path.resolve('./static/scripts/'),
    filename: '[name].js',
  },

  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new webpack.LoaderOptionsPlugin({
      minimize: true,
      debug: false
    }),
    // new ExtractTextPlugin('public/style.css', {
    //   allChunks: true
    // }),
  ],

  module: {
    rules: [
      { 
        test: /\.jsx?$/,
        exclude: /node_modules/, 
        loader: 'babel-loader',
        options: {
          presets:[
            ['es2015', {modules: false}], 
            'react'
          ],
        },
      }, {
        test: /\.scss$/,
        loaders: ['style', 'css', 'sass']
      },
    ],
  },

  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js', '.jsx']
  },
};
