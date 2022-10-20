import * as Sentry from "https://cdn.skypack.dev/@sentry/browser";
import { BrowserTracing } from "https://cdn.skypack.dev/@sentry/tracing";

const head = document.querySelector("head");
const DSN = head.dataset.sentryDsn;

if (DSN.length > 0 && DSN.startsWith("https://")) {
    Sentry.init({
        dsn: DSN,
        integrations: [new BrowserTracing()],
        release: head.dataset.sentryRelease,
    });

    Sentry.setUser({ email: head.dataset.sentryEmail });
}
