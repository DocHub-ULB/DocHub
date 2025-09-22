import * as Sentry from "https://cdn.jsdelivr.net/npm/@sentry/browser@8.34.0+esm";

const head = document.querySelector("head");
const DSN = head.dataset.sentryDsn;

if (DSN.length > 0 && DSN.startsWith("https://")) {
    Sentry.init({
        dsn: DSN,
        integrations: [Sentry.browserTracingIntegration()],
        release: head.dataset.sentryRelease,
    });

    Sentry.setUser({ email: head.dataset.sentryEmail });
}
