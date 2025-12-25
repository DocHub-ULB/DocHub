import _ from 'https://cdn.jsdelivr.net/npm/lodash@4.17.21/+esm';

import {Controller, Application} from 'https://cdn.jsdelivr.net/npm/@hotwired/stimulus@3.2.2/+esm';
import {Autocomplete} from 'https://cdn.jsdelivr.net/npm/stimulus-autocomplete@3.1.0/+esm';
import tomSelect from 'https://cdn.jsdelivr.net/npm/tom-select@2.4.3/+esm';

function normalize(s) {
    let r = s.toLowerCase();
    r = r.replace(new RegExp("\\s", 'g'), "");
    r = r.replace(new RegExp("[àáâãäå]", 'g'), "a");
    r = r.replace(new RegExp("æ", 'g'), "ae");
    r = r.replace(new RegExp("ç", 'g'), "c");
    r = r.replace(new RegExp("[èéêë]", 'g'), "e");
    r = r.replace(new RegExp("[ìíîï]", 'g'), "i");
    r = r.replace(new RegExp("ñ", 'g'), "n");
    r = r.replace(new RegExp("[òóôõö]", 'g'), "o");
    r = r.replace(new RegExp("œ", 'g'), "oe");
    r = r.replace(new RegExp("[ùúûü]", 'g'), "u");
    r = r.replace(new RegExp("[ýÿ]", 'g'), "y");
    r = r.replace(new RegExp("\\W", 'g'), "");
    return r;
}

function humanFileSize(bytes, dp = 1) {
    const thresh = 1000;

    if (Math.abs(bytes) < thresh) {
        return bytes + ' B';
    }

    const units = ['kB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
    let u = -1;
    const r = 10 ** dp;

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
    static targets = ["query", "tag", "filterable"]

    filter(event) {
        let normalizedFilterTerm = normalize(this.queryTarget.value)
        let selectedTags = this.tagTargets
            .filter((el) => el.checked)
            .map((el) => el.getAttribute("data-tag-name"));

        this.filterableTargets.forEach((el, i) => {
            let key = el.getAttribute("data-filter-key");
            let tags = el.getAttribute("data-tags").split(" ");

            let normalizedTitle = normalize(key)

            let containsText = normalizedTitle.includes(normalizedFilterTerm);
            let containsTags = _.difference(selectedTags, tags).length === 0;
            el.classList.toggle("d-none", !containsText || !containsTags)
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

import {getDocument, GlobalWorkerOptions} from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/+esm';
GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/build/pdf.worker.mjs"


class Viewer extends Controller {
    static targets = ["renderer", "loader"]
    static values = {src: String, loaded: Boolean, error: Boolean}
    pageSizeLogDebounce = false;

    static options = {
        threshold: 0, // default
    }


    async connect() {
        let loadingTask = getDocument(this.srcValue);

        loadingTask.onProgress = async (data) => {
            let percent = Math.round(data.loaded / data.total * 100)
            this.loaderTarget.setAttribute("value", percent);
        }

        try {
            this.pdf = await loadingTask.promise;
        } catch (e) {
            console.log("Error while loading remote PDF", e);
            this.errorValue = true;
            this.loadedValue = true;
            return;
        }

        this.loadedValue = true;

        console.log("PDF loaded with ", this.pdf.numPages, " pages");
        console.debug(this.pdf);

        this.pages = {};

        let options = {
            rootMargin: '0px',
            threshold: 0
        }

        this.observer = new IntersectionObserver(this.intersectionCallback.bind(this), options);

        let wrappers = [];

        for (let i = 1; i <= this.pdf.numPages; i++) {
            this.pages[i] = await this.pdf.getPage(i);

            let wrapper = document.createElement("div");
            wrapper.classList.add("page-wrapper");
            wrapper.style['aspectRatio'] = this.getPageRatio(i);
            wrapper.setAttribute("data-viewer-page-param", i)

            wrappers.push(wrapper);
            this.rendererTarget.appendChild(wrapper);

        }

        // only add all the pages to the observer after they are all created so we
        // avoid listening to all the events while the pages are being created
        // and the DOM reflows each time
        wrappers.map((el) => this.observer.observe(el));

    }

    intersectionCallback(event) {
        event.map(entry => {
            let wrapper = entry.target
            let pageNumber = parseInt(wrapper.getAttribute("data-viewer-page-param"))
            let isRendered = wrapper.getElementsByTagName("canvas")[0] !== undefined;

            if (!isRendered && entry.isIntersecting) {
                console.log("Rendering page", pageNumber)
                this.renderPage(pageNumber, wrapper);
            }
            if (isRendered && !entry.isIntersecting) {
                console.log("Removing page", pageNumber)
                this.removePage(wrapper);
            }
        })
    }

    getPageSizes(i) {
        let page = this.pages[i];
        let viewport = page.getViewport({scale: 1,});

        // retina support
        let screenRatio = window.devicePixelRatio || 1

        let scale = screenRatio * (this.rendererTarget.clientWidth / viewport.width)

        let width = Math.floor(viewport.width * scale);
        let height = Math.floor(viewport.height * scale);

        if (!this.pageSizeLogDebounce) {
            this.pageSizeLogDebounce = true;
            console.log(`Page ${i} canvas resolution is ${width}x${height}`)
        }
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
        if (canvas !== undefined) canvas.remove();
        wrapper.removeAttribute("data-viewer-ready")
    }
}

class Upload extends Controller {
    static targets = ["input", "inputwrapper", "name", "originalname", "size", "form"]

    input(event) {
        console.log("File upload", event);
        let files = this.inputTarget.files;
        if (files.length > 0) {
            this.inputTarget.setAttribute("filled", "")
            let file = files[0];
            this.nameTarget.value = cleanName(file.name)
            this.originalnameTarget.textContent = file.name
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
        this.inputwrapperTarget.setAttribute("active", "")
    }

    leave(event) {
        if (event !== null) {
            event.preventDefault()
        }
        this.inputwrapperTarget.removeAttribute("active")
    }

}

class TomSelect extends Controller {
    async connect() {
        new tomSelect(this.element, {hidePlaceholder: true});
    }
}

class Share extends Controller {
    static values = {
        shareUrl: String
    }

    connect() {
        if ("share" in navigator) {
            this.element.classList.remove("d-none")
        }
    }

    async share() {
        const url = new URL(this.shareUrlValue, window.location);
        console.log("Sharing", url.href)
        try {
            await navigator.share({
                url: url.href,
            })
        } catch (error) {
            if (error.toString().includes('AbortError')) {
                // Yes, checking the string representation of the error is hideous,
                // but I don't know how to do better and AbortError is undefined
                console.info("Share aborted by user")
            } else {
                throw error;
            }
        }
    }

}

class Modal extends Controller {
    close() {
        this.element.close();
    }
}

class ModalTrigger extends Controller {
    static values = {
        target: String
    }

    open(event) {
        // Allow browser default behavior when modifier keys are pressed
        // (Ctrl+click, Cmd+click, Shift+click, or middle-click)
        if (event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1) {
            return;
        }

        event.preventDefault();
        const dialog = document.getElementById(this.targetValue);
        if (dialog) {
            dialog.showModal();
        }
    }
}

const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("search", Search);
application.register("viewer", Viewer);
application.register("upload", Upload);
application.register('autocomplete', Autocomplete);
application.register('tom-select', TomSelect);
application.register('share', Share);
application.register('modal', Modal);
application.register('modal-trigger', ModalTrigger);

application.debug = true;
