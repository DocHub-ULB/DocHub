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

import {getDocument, GlobalWorkerOptions} from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/build/pdf.min.mjs';
GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/build/pdf.worker.mjs"


class Viewer extends Controller {
    static targets = ["renderer", "loader"]
    static outlets = ["pager"]
    static values = {src: String, loaded: Boolean, error: Boolean}
    pageSizeLogDebounce = false;
    currentPage = 0;

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

        if (this.hasPagerOutlet) this.pagerOutlet.setTotal(this.pdf.numPages);

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

        this.onScroll = this.onScroll.bind(this);
        window.addEventListener("scroll", this.onScroll, {passive: true});
        window.addEventListener("resize", this.onScroll);
        this.updateCurrentPage();
    }

    disconnect() {
        window.removeEventListener("scroll", this.onScroll);
        window.removeEventListener("resize", this.onScroll);
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

    // The current page is the one crossing a reference line just below the pinbar
    // (not merely the topmost visible one — otherwise a sliver of the previous
    // page left showing above would keep the count a page behind). Throttled to
    // one computation per animation frame.
    onScroll() {
        if (this.scrollScheduled) return;
        this.scrollScheduled = true;
        requestAnimationFrame(() => {
            this.scrollScheduled = false;
            this.updateCurrentPage();
        });
    }

    updateCurrentPage() {
        // Reference line, in px below the viewport top, that decides the current
        // page: kept below the fixed pinbar so a jumped-to page reads as current
        // rather than the sliver of the previous one still showing above it.
        let ref = 96;
        let current = 0;
        for (let wrapper of this.rendererTarget.children) {
            let rect = wrapper.getBoundingClientRect();
            if (rect.top <= ref && rect.bottom > ref) {
                current = parseInt(wrapper.getAttribute("data-viewer-page-param"));
                break;
            }
        }
        if (!current || current === this.currentPage) return;
        this.currentPage = current;
        if (this.hasPagerOutlet) this.pagerOutlet.setCurrent(current);
    }

    // Called by the pager when the reader types a page number or steps through.
    goToPage(pageNumber) {
        if (!this.pdf) return;
        let page = Math.min(Math.max(pageNumber, 1), this.pdf.numPages);
        let wrapper = this.rendererTarget
            .querySelector(`[data-viewer-page-param="${page}"]`);
        if (wrapper) wrapper.scrollIntoView({behavior: "smooth", block: "start"});
    }

    // When the pager connects, hand it whatever we already know so it isn't stuck
    // showing placeholders if the PDF finished loading first.
    pagerOutletConnected(pager) {
        if (this.pdf) pager.setTotal(this.pdf.numPages);
        if (this.currentPage) pager.setCurrent(this.currentPage);
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

class Disclosure extends Controller {
    connect() {
        this.onClickOutside = this.onClickOutside.bind(this);
        document.addEventListener("click", this.onClickOutside);
    }

    disconnect() {
        document.removeEventListener("click", this.onClickOutside);
    }

    onClickOutside(event) {
        if (this.element.open && !this.element.contains(event.target)) {
            this.element.open = false;
        }
    }
}

class Chart extends Controller {
    static values = {
        data: Array,
        label: String,
        labelsId: String,
    }

    async connect() {
        const ChartJS = (await import('https://cdn.jsdelivr.net/npm/chart.js@4.4.4/auto/+esm')).default;

        const labels = JSON.parse(document.getElementById(this.labelsIdValue).textContent);

        this.chart = new ChartJS(this.element, {
            type: "line",
            data: {
                labels,
                datasets: [{
                    label: this.labelValue,
                    data: this.dataValue,
                    borderColor: "#0d6efd",
                    backgroundColor: "rgba(13, 110, 253, 0.1)",
                    fill: true,
                    tension: 0,
                    pointRadius: 0,
                    borderWidth: 1.5,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2.5,
                animation: false,
                interaction: {mode: "index", intersect: false},
                plugins: {legend: {display: false}},
                scales: {
                    y: {beginAtZero: true, ticks: {precision: 0}},
                    x: {ticks: {maxTicksLimit: 8, maxRotation: 0}},
                },
            },
        });
    }

    disconnect() {
        if (this.chart) {
            this.chart.destroy();
        }
    }
}

// Reveals a slim fixed toolbar (the pinbar) once the full viewer action bar has
// scrolled out of view, so the download button stays reachable. The full bar
// scrolls away in normal flow and the pinbar is a fixed overlay — no reserved
// space, so nothing below ever reflows and slow scrolling never jumps.
class StickyBar extends Controller {
    static targets = ["bar", "pin"]

    connect() {
        this.topbar = document.querySelector(".topbar");
        this.update = this.update.bind(this);
        window.addEventListener("scroll", this.update, {passive: true});
        window.addEventListener("resize", this.update);
        this.update();
    }

    // The pinbar sits below the topbar only while it's sticky/fixed; on the
    // viewer the topbar is static and scrolls away, so the offset is 0.
    offset() {
        if (!this.topbar) return 0;
        let pos = getComputedStyle(this.topbar).position;
        return pos === "sticky" || pos === "fixed" ? this.topbar.offsetHeight : 0;
    }

    update() {
        if (!this.hasPinTarget) return;
        let bottom = this.barTarget.getBoundingClientRect().bottom;
        this.pinTarget.classList.toggle("is-visible", bottom <= this.offset());
    }

    disconnect() {
        window.removeEventListener("scroll", this.update);
        window.removeEventListener("resize", this.update);
    }
}

// The page indicator in the viewer pinbar: shows "current / total" and lets the
// reader jump to a page. It drives the viewer through the `viewer` outlet and is
// driven back by it (setCurrent / setTotal) as the document scrolls.
class Pager extends Controller {
    static targets = ["input", "total"]
    static outlets = ["viewer"]

    setCurrent(page) {
        // Don't fight the reader while they're typing into the field.
        if (document.activeElement !== this.inputTarget) {
            this.inputTarget.value = page;
        }
    }

    setTotal(total) {
        this.totalTarget.textContent = total;
    }

    goto(event) {
        event.preventDefault();
        let page = parseInt(this.inputTarget.value, 10);
        if (!isNaN(page) && this.hasViewerOutlet) this.viewerOutlet.goToPage(page);
        this.inputTarget.blur();
    }

    prev() {
        this.step(-1);
    }

    next() {
        this.step(1);
    }

    step(delta) {
        let page = parseInt(this.inputTarget.value, 10) || 1;
        if (this.hasViewerOutlet) this.viewerOutlet.goToPage(page + delta);
    }
}

const application = Application.start()

application.register("course-filter", CourseFilter);
application.register("sticky-bar", StickyBar);
application.register("search", Search);
application.register("viewer", Viewer);
application.register("pager", Pager);
application.register("upload", Upload);
application.register('autocomplete', Autocomplete);
application.register('tom-select', TomSelect);
application.register('share', Share);
application.register('modal', Modal);
application.register('modal-trigger', ModalTrigger);
application.register('chart', Chart);
application.register('disclosure', Disclosure);

application.debug = true;
