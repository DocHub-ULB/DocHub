const webpack = require('webpack');
const config = require('./webpack.base.config.js');
const OptimizeCssAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const PrepackWebpackPlugin = require('prepack-webpack-plugin').default;
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

config.plugins = config.plugins.concat([
  new webpack.DefinePlugin({
    'process.env': {
      NODE_ENV: JSON.stringify('production')
    }
  }),
  new UglifyJsPlugin({}),
]);

module.exports = config;
