import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/stimulus';

const application = Application.start()


class Filter extends Controller {
    static targets = [ "source", "filterable" ]

    filter(event) {
      let lowerCaseFilterTerm = this.sourceTarget.value.toLowerCase()

      this.filterableTargets.forEach((el, i) => {
        let filterableKey =  el.getAttribute("data-filter-key")
        el.classList.toggle("filter--filtered", !filterableKey.toLowerCase().includes( lowerCaseFilterTerm ) )
    })
  }
}

application.register("filter", Filter);
