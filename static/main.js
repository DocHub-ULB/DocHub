import _ from 'https://cdn.jsdelivr.net/npm/lodash@4.17.21/+esm';
import tomSelect from 'https://cdn.jsdelivr.net/npm/tom-select@2.4.3/+esm';
import {getDocument, GlobalWorkerOptions} from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/+esm';

GlobalWorkerOptions.workerSrc = "https://cdn.jsdelivr.net/npm/pdfjs-dist@5.4.449/build/pdf.worker.mjs"

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
    // Returns the name without dashes, underscores and removes the extension
    return name.replace(/[-_]/g, ' ').replace(/\.[^.]+$/, '');
}


// Alpine.js components
document.addEventListener('alpine:init', () => {

    // Course filter: client-side filtering of documents by text query and tags
    Alpine.data('courseFilter', () => ({
        filter() {
            const query = this.$refs.query ? this.$refs.query.value : '';
            const normalizedQuery = normalize(query);

            const tags = Array.from(this.$el.querySelectorAll('[data-tag-name]'))
                .filter(el => el.checked)
                .map(el => el.getAttribute('data-tag-name'));

            this.$el.querySelectorAll('[data-filter-key]').forEach(el => {
                const key = el.getAttribute('data-filter-key');
                const elTags = el.getAttribute('data-tags').split(' ');
                const normalizedTitle = normalize(key);

                const containsText = normalizedTitle.includes(normalizedQuery);
                const containsTags = _.difference(tags, elTags).length === 0;
                el.classList.toggle('d-none', !containsText || !containsTags);
            });
        }
    }));

    // Upload: file upload with drag-and-drop preview
    Alpine.data('upload', () => ({
        dragging: false,

        handleFile(event) {
            const files = this.$refs.input.files;
            if (files.length > 0) {
                this.$refs.input.setAttribute('filled', '');
                const file = files[0];
                this.$refs.name.value = cleanName(file.name);
                this.$refs.originalname.textContent = file.name;
                this.$refs.size.textContent = humanFileSize(file.size);
                this.$refs.form.classList.remove('upload--hide');
            } else {
                this.$refs.input.removeAttribute('filled');
                this.$refs.form.classList.add('upload--hide');
            }
            this.dragging = false;
        },

        enter(event) {
            event.preventDefault();
            this.dragging = true;
        },

        leave(event) {
            event.preventDefault();
            this.dragging = false;
        }
    }));

    // Share: Web Share API
    Alpine.data('share', (shareUrl) => ({
        supported: false,

        init() {
            this.supported = 'share' in navigator;
        },

        async doShare() {
            const url = new URL(shareUrl, window.location);
            console.log('Sharing', url.href);
            try {
                await navigator.share({ url: url.href });
            } catch (error) {
                if (error.toString().includes('AbortError')) {
                    console.info('Share aborted by user');
                } else {
                    throw error;
                }
            }
        }
    }));

    // Modal trigger: opens a <dialog> element
    Alpine.data('modalTrigger', (targetId) => ({
        open(event) {
            if (event.ctrlKey || event.metaKey || event.shiftKey || event.button === 1) {
                return;
            }
            event.preventDefault();
            const dialog = document.getElementById(targetId);
            if (dialog) {
                dialog.showModal();
            }
        }
    }));
});


// PDF Viewer: initialized via data attribute, not Alpine (too complex for Alpine's reactive model)
function initViewer(el) {
    const src = el.dataset.viewerSrc;
    const renderer = el.querySelector('[data-viewer-renderer]');
    const loader = el.querySelector('[data-viewer-loader]');

    let pages = {};
    let pageSizeLogDebounce = false;

    async function load() {
        const loadingTask = getDocument(src);

        loadingTask.onProgress = (data) => {
            const percent = Math.round(data.loaded / data.total * 100);
            loader.setAttribute('value', percent);
        };

        let pdf;
        try {
            pdf = await loadingTask.promise;
        } catch (e) {
            console.log('Error while loading remote PDF', e);
            el.setAttribute('data-error', '');
            el.setAttribute('data-loaded', '');
            return;
        }

        el.setAttribute('data-loaded', '');

        console.log('PDF loaded with', pdf.numPages, 'pages');
        console.debug(pdf);

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                const wrapper = entry.target;
                const pageNumber = parseInt(wrapper.getAttribute('data-page'));
                const isRendered = wrapper.getElementsByTagName('canvas')[0] !== undefined;

                if (!isRendered && entry.isIntersecting) {
                    console.log('Rendering page', pageNumber);
                    renderPage(pageNumber, wrapper);
                }
                if (isRendered && !entry.isIntersecting) {
                    console.log('Removing page', pageNumber);
                    removePage(wrapper);
                }
            });
        }, { rootMargin: '0px', threshold: 0 });

        const wrappers = [];

        for (let i = 1; i <= pdf.numPages; i++) {
            pages[i] = await pdf.getPage(i);

            const wrapper = document.createElement('div');
            wrapper.classList.add('page-wrapper');
            wrapper.style['aspectRatio'] = getPageRatio(i);
            wrapper.setAttribute('data-page', i);

            wrappers.push(wrapper);
            renderer.appendChild(wrapper);
        }

        wrappers.forEach(w => observer.observe(w));
    }

    function getPageSizes(i) {
        const page = pages[i];
        const viewport = page.getViewport({ scale: 1 });
        const screenRatio = window.devicePixelRatio || 1;
        const scale = screenRatio * (renderer.clientWidth / viewport.width);
        const width = Math.floor(viewport.width * scale);
        const height = Math.floor(viewport.height * scale);

        if (!pageSizeLogDebounce) {
            pageSizeLogDebounce = true;
            console.log(`Page ${i} canvas resolution is ${width}x${height}`);
        }
        return { width, height, scale };
    }

    function getPageRatio(i) {
        const { width, height } = getPageSizes(i);
        return `${width} / ${height}`;
    }

    async function renderPage(i, wrapper) {
        const canvas = document.createElement('canvas');
        wrapper.appendChild(canvas);

        const page = pages[i];
        const { width, height, scale } = getPageSizes(i);

        canvas.width = width;
        canvas.height = height;
        canvas.style.width = '100%';

        const renderContext = {
            canvasContext: canvas.getContext('2d'),
            transform: [scale, 0, 0, scale, 0, 0],
            viewport: page.getViewport({ scale: 1 }),
        };
        await page.render(renderContext);

        wrapper.setAttribute('data-viewer-ready', '');
    }

    function removePage(wrapper) {
        const canvas = wrapper.getElementsByTagName('canvas')[0];
        if (canvas !== undefined) canvas.remove();
        wrapper.removeAttribute('data-viewer-ready');
    }

    load();
}

// Initialize viewers on page load and after htmx swaps
function initViewers() {
    document.querySelectorAll('[data-viewer-src]:not([data-viewer-initialized])').forEach(el => {
        el.setAttribute('data-viewer-initialized', '');
        initViewer(el);
    });
}

// Initialize tom-select widgets
function initTomSelects() {
    document.querySelectorAll('[data-tom-select]:not([data-tom-select-initialized])').forEach(el => {
        el.setAttribute('data-tom-select-initialized', '');
        new tomSelect(el, { hidePlaceholder: true });
    });
}

// Run initializers on page load and after htmx content swaps
document.addEventListener('DOMContentLoaded', () => {
    initViewers();
    initTomSelects();
});

document.addEventListener('htmx:afterSettle', () => {
    initViewers();
    initTomSelects();
});
