# Mostly copied from
# https://github.com/unoconv/unoserver-docker/blob/main/Dockerfile
# Under MIT License Copyright (c) 2022 unoconv

FROM eclipse-temurin:24.0.1_9-jdk-alpine-3.21

LABEL org.opencontainers.image.source=https://github.com/DocHub-ULB/DocHub/unoserver

# Install LibreOffice, Python, and essential dependencies
RUN apk add --no-cache \
    py3-pip \
    libreoffice \
    # Essential fonts for document rendering
    font-noto \
    font-noto-cjk \
    ttf-dejavu \
    ttf-liberation \
    fontconfig && \
    fc-cache -f && \
    rm -rf /var/cache/apk/* /tmp/*

# Install unoserver
RUN pip install --break-system-packages unoserver==3.6

# Create non-root user
RUN addgroup -S worker && adduser -S worker -G worker
USER worker
WORKDIR /home/worker

# Expose unoserver port
EXPOSE 2003

HEALTHCHECK --interval=5s CMD unoping --host 127.0.0.1 --port 2003

# Run unoserver
CMD ["unoserver", "--interface", "0.0.0.0", "--port", "2003"]

