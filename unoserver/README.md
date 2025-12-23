# Unoserver Docker Image

This Docker image is used as a service in our GitHub Actions workflow for running tests (see `.github/workflows/python-tests.yml`).

To build and push the image: `docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/dochub-ulb/unoserver:latest . --push`
