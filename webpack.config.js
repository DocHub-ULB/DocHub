var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');                                                                                                                           
var webpack = require('webpack');

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
