import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';

const application = Application.start()

function normalize(s){
    let r=s.toLowerCase();
    r = r.replace(new RegExp("\\s", 'g'),"");
    r = r.replace(new RegExp("[àáâãäå]", 'g'),"a");
    r = r.replace(new RegExp("æ", 'g'),"ae");
    r = r.replace(new RegExp("ç", 'g'),"c");
    r = r.replace(new RegExp("[èéêë]", 'g'),"e");
    r = r.replace(new RegExp("[ìíîï]", 'g'),"i");
    r = r.replace(new RegExp("ñ", 'g'),"n");
    r = r.replace(new RegExp("[òóôõö]", 'g'),"o");
    r = r.replace(new RegExp("œ", 'g'),"oe");
    r = r.replace(new RegExp("[ùúûü]", 'g'),"u");
    r = r.replace(new RegExp("[ýÿ]", 'g'),"y");
    r = r.replace(new RegExp("\\W", 'g'),"");
    return r;
};


class CourseFilter extends Controller {
    static targets = [ "query", "tag", "filterable" ]

    filter(event) {
      let normalizedFilterTerm = normalize(this.queryTarget.value)
      let selectedTags = this.tagTargets
        .filter((el) => el.checked)
        .map((el) => el.getAttribute("data-tag-name"));

      this.filterableTargets.forEach((el, i) => {
        let key =  el.getAttribute("data-filter-key");
        let tags = el.getAttribute("data-tags").split(" ");

        let normalizedTitle = normalize(key)

        let containsText = normalizedTitle.includes(normalizedFilterTerm);
        let containsTags = _.difference(selectedTags, tags).length === 0;
        el.classList.toggle("filter--filtered", !containsText || !containsTags)
    })
  }
}

class Search extends Controller {
    static targets = ["input", "output", "submit"]

    initialize() {
      this.search = _.debounce(this.search, 200, {trailing: true})
    }

    search(event) {
      this.outputTarget.value = this.inputTarget.value
      this.submitTarget.click();
    }
}

application.register("course-filter", CourseFilter);
application.register("search", Search);
