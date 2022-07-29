import _ from 'https://cdn.skypack.dev/lodash';

import hotwiredTurbo from 'https://cdn.skypack.dev/@hotwired/turbo';
import {Controller, Application} from 'https://cdn.skypack.dev/@hotwired/stimulus';

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
    static targets = ["renderer", "loader"]
    static values = {src: String, loaded: Boolean}

    static options = {
        threshold: 0, // default
    }

    async connect() {
        let loadingTask = pdfjs.getDocument(this.srcValue);

        loadingTask.onProgress = async (data) => {
            let percent = Math.round(data.loaded / data.total * 100)
            this.loaderTarget.setAttribute("value", percent);
        }
        this.pdf = await loadingTask.promise;
        this.loadedValue = true;

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

    getPageSizes(i) {
        let page = this.pages[i];
        let viewport = page.getViewport({scale: 1,});


        // retina support
        let screenRatio = window.devicePixelRatio || 1

        let scale = screenRatio * Math.max(this.rendererTarget.clientWidth / viewport.width, this.rendererTarget.clientHeight / viewport.height)

        let width = Math.floor(viewport.width * scale);
        let height = Math.floor(viewport.height * scale);
        return {width, height, scale}
    }

    getPageRatio(i) {
        const {width, height} = this.getPageSizes(i)
        return `${width} / ${height}`;
    }

    async renderPage(i, wrapper) {

        let canvas = document.createElement("canvas")
        wrapper.appendChild(canvas);

        let page = this.pages[i];

        const {width, height, scale} = this.getPageSizes(i)

        canvas.width = width
        canvas.height = height
        canvas.style.width = "100%";

        // Render PDF page into canvas context.
        let renderContext = {
            canvasContext: canvas.getContext('2d'),
            transform: [scale, 0, 0, scale, 0, 0],
            viewport: page.getViewport({scale: 1,}),
        };
        await page.render(renderContext);

        wrapper.setAttribute("data-viewer-ready", "")
    }

    removePage(wrapper) {
        let canvas = wrapper.getElementsByTagName("canvas")[0]
        if(canvas !== undefined) canvas.remove();
        wrapper.removeAttribute("data-viewer-ready")
    }

}

const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("viewer", Viewer);
application.debug = true;
