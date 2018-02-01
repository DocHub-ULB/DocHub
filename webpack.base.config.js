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
    viewer: [
      './assets/viewer/index.js',
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
    new webpack.optimize.CommonsChunkPlugin({
      name: 'commons',
      filename: '[name]-[hash].js',
      minChunks: 2,
    }),
  ],

  module: {
    rules: [
      {
        test: [/\.jsx?$/, /\.js?$/, ],
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
        loaders: [
          'style-loader',
          'css-loader',
        ],
      },
      {
        test: /\.sass?$/,
        loaders: ['style-loader', 'css-loader', 'sass-loader']
      },
    ],
  },

  resolve: {
    modules: ['node_modules', 'bower_components'],
    extensions: ['.js', '.jsx']
  },
};
