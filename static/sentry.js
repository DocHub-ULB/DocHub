import * as Sentry from "https://cdn.skypack.dev/@sentry/browser";
import { BrowserTracing } from "https://cdn.skypack.dev/@sentry/tracing";

const head = document.querySelector("head");
const DSN = head.dataset.sentryDsn;

Sentry.init({
    dsn: DSN,
    integrations: [new BrowserTracing()],
});
