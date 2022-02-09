import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';

const application = Application.start()

function humanFileSize(bytes, dp=1) {
    const thresh = 1000;

    if (Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }

    const units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    let u = -1;
    const r = 10**dp;

    do {
        bytes /= thresh;
        ++u;
    } while (Math.round(Math.abs(bytes) * r) / r >= thresh && u < units.length - 1);


    return bytes.toFixed(dp) + ' ' + units[u];
}

function cleanName(name) {
    // Returns the name withtout dashes, underscores and removes the extension
    return name.replace(/[-_]/g, ' ').replace(/\.[^.]+$/, '');

}


class CourseFilter extends Controller {
    static targets = [ "query", "tag", "filterable" ]

    filter(event) {
      let lowerCaseFilterTerm = this.queryTarget.value.toLowerCase()
      let selectedTags = this.tagTargets
        .filter((el) => el.checked)
        .map((el) => el.getAttribute("data-tag-name"));

      this.filterableTargets.forEach((el, i) => {
        let key =  el.getAttribute("data-filter-key");
        let tags = el.getAttribute("data-tags").split(" ");
        let containsText = key.toLowerCase().includes( lowerCaseFilterTerm );
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


class Upload extends Controller {
    static targets = ["input", "name", "size", "form"]

    input(event) {
        console.log("File upload", event);
        let files = this.inputTarget.files;
        if (files.length > 0) {
            this.inputTarget.setAttribute("filled", "")
            let file = files[0];
            this.nameTarget.value = cleanName(file.name)
            this.sizeTarget.textContent = humanFileSize(file.size);

            this.formTarget.classList.remove("upload--hide")
        } else {
            this.inputTarget.removeAttribute("filled")
            this.formTarget.classList.add("upload--hide")
        }
        this.leave(null);
    }

    enter(event) {
        event.preventDefault()
        this.inputTarget.setAttribute("active" , "")
    }

    leave(event) {
        if(event !== null) { event.preventDefault() }
        this.inputTarget.removeAttribute("active")
    }

}

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("upload", Upload);

application.debug = true;
