import * as Sentry from "https://unpkg.com/@sentry/browser@7.108.0?module";
import { BrowserTracing } from "https://unpkg.com/@sentry/tracing@7.108.0?module";

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
