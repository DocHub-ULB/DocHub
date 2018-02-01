const config = require('./webpack.base.config.js');

config.devtool = 'eval-source-map';

module.exports = config;
