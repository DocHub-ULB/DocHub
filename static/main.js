import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';
import { useIntersection } from 'https://cdn.skypack.dev/stimulus-use'

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
    static values = {src: String, hasPage: Boolean}

    static options = {
        threshold: 0, // default
    }

    async connect() {
        let loadingTask = pdfjs.getDocument(this.srcValue);

        loadingTask.onProgress = (data) => {
            //this.loaderTarget.setAttribute("value", 100 * data.loaded / data.total);
        }

        this.pdf = await loadingTask.promise;
        console.log("PDF loaded")
        this.pages = {};

        let options = {
            root: this.element,
            rootMargin: '0px',
            threshold: 0
        }
        let callback = (event) => {
            event.map(entry => {
                let wrapper = entry.target
                let pageNumber = parseInt(wrapper.getAttribute("data-viewer-page-param"))
                let isRendered = wrapper.getElementsByTagName("canvas")[0] !== undefined;

                if(!isRendered && entry.isIntersecting) {
                    console.log("rendering page", pageNumber)
                    this.renderPage(pageNumber, wrapper);
                }
                if(isRendered && !entry.isIntersecting) {
                    console.log("Removing page", pageNumber)
                    this.removePage(wrapper);
                }
            })
        }

        this.observer = new IntersectionObserver(callback, options);

        for (let i = 1; i <= this.pdf.numPages; i++) {
            this.pages[i] = await this.pdf.getPage(i);

            let wrapper = document.createElement("div");
            wrapper.classList.add("page-wrapper");
            wrapper.style['aspectRatio'] = this.getPageRatio(i);
            wrapper.setAttribute("data-viewer-page-param", i)
            this.observer.observe(wrapper)

            this.rendererTarget.appendChild(wrapper);

        }

    }

    getPageSize(i) {}

    getPageRatio(i) {
        let page = this.pages[i];
        let viewport = page.getViewport({scale: 1,});
        return `${viewport.width} / ${viewport.height}`;
    }

    async renderPage(i, wrapper) {

        let canvas = document.createElement("canvas")
        wrapper.appendChild(canvas);

        let page = await this.pdf.getPage(i);
        let viewport = page.getViewport({scale: 1,});

        // retina support
        let screenRatio = window.devicePixelRatio || 1

        let scale = screenRatio * Math.max(window.innerWidth / viewport.width, window.innerHeight / viewport.height)

        canvas.width = Math.floor(viewport.width * scale);
        canvas.height = Math.floor(viewport.height * scale);
        canvas.style.width = "100%";

        let transform = scale !== 1
            ? [scale, 0, 0, scale, 0, 0]
            : null;

        // Render PDF page into canvas context.
        let renderContext = {
            canvasContext: canvas.getContext('2d'),
            transform,
            viewport,
        };
        await page.render(renderContext);

        if(i < 2) {
            // The page might be loading while being visible in the viewport
            // se we want to make sure that the browser has rendered the canvas
            // before starting the reveal animation
            await new Promise((resolve) => setTimeout(resolve, 10));
        }

        canvas.setAttribute("data-viewer-ready", "")
    }

    removePage(wrapper) {
        let canvas = wrapper.getElementsByTagName("canvas")[0]
            if(canvas !== undefined) canvas.remove();
    }

}

const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("viewer", Viewer);
application.debug = true;
