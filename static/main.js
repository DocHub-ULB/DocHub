import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';

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

import bundledEsModulesPdfjsDist from 'https://cdn.skypack.dev/@bundled-es-modules/pdfjs-dist@2.5.207-rc1';
let pdfjs = bundledEsModulesPdfjsDist
pdfjs.GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@2.5.207/build/pdf.worker.js"


class Viewer extends Controller {
    static targets = ["renderer"]
    static values = {src: String}

    async connect() {
        this.pdf = await pdfjs.getDocument(this.srcValue).promise;

        var page = await this.pdf.getPage(1);
        var scale = 0.9;
        var viewport = page.getViewport({scale: scale,});
        
        // Support HiDPI-screens.
        var outputScale = window.devicePixelRatio || 1;

        // Prepare canvas using PDF page dimensions.
        var canvas = this.rendererTarget;
        var context = canvas.getContext('2d');

        canvas.width = Math.floor(viewport.width * outputScale);
        canvas.height = Math.floor(viewport.height * outputScale);
        canvas.style.width = Math.floor(viewport.width) + "px";
        canvas.style.height = Math.floor(viewport.height) + "px";

        var transform = outputScale !== 1
            ? [outputScale, 0, 0, outputScale, 0, 0]
            : null;

        // Render PDF page into canvas context.
        var renderContext = {
            canvasContext: context,
            transform,
            viewport,
        };
        page.render(renderContext);

    }

}







const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("viewer", Viewer);
application.debug = true;
