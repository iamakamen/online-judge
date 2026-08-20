FROM alpine:3.22

RUN apk add --no-cache curl \
    && addgroup -S runner \
    && adduser -S -G runner -u 1000 runner

USER runner:runner

WORKDIR /workspace

ENTRYPOINT ["/bin/sh"]
