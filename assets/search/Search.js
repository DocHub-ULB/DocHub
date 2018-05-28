import React from 'react';
import Select from 'react-select';
import 'react-select/dist/react-select.css';
import axios from 'axios';

const URL = "/api/search/courses/";

export default class Search extends React.Component {
  constructor (props) {
    super(props);

    this.state = {
      value: '',
      options: [],
    };

    this.handleChange = this.handleChange.bind(this);
  }

  handleChange (value) {
		window.location.href = `/catalog/course/${value.slug}`;
  }

  gotoCourse (value, event) {
		window.location.href = value.url;
  }

  getCourses (input) {
		if (!input) {
			return Promise.resolve({ options: [] });
		}

		return axios.get(`${URL}?query=${input}`)
  		.then(response => ({ options: response.data }));
  }

  renderOption (option) {
      return (
          <span>
              <span className="course-label secondary radius label recent-blob fixed-label">
                {option.slug}
              </span>&nbsp;
             {option.name}
          </span>
      );
  }

  render() {
    return (
      <Select.Async
        multi={false}
        value={this.state.value}
        onChange={this.handleChange}
        onValueClick={this.gotoCourse}
        valueKey="slug"
        labelKey="name"
        loadOptions={this.getCourses}
        backspaceRemoves={true}
        optionRenderer={this.renderOption}
        placeholder="Chercher un cours (exemple: info-f-101 ou Microéconomie)"
        searchPromptText="Écrivez pour rechercher"
      />
    );
  }
}
