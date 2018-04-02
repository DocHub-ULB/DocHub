import React from 'react';
import { render } from 'react-dom';

import Cookies from 'js-cookie'

import Uploader from './Uploader';

const data = document.getElementById('react-data').dataset
const csrftoken = Cookies.get('csrftoken');

fetch('/api/tags', { credentials: "same-origin"})
.then(function(response) {
    return response.json();
})
.then(function(tags) {
    render(
      <Uploader slug={data.slug} name={data.name} crsf={csrftoken} tags={tags}/>,
      document.getElementById('root')
    );
});
